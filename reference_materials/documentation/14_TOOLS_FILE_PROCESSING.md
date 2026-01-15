# 14. Tools - File Processing

## Przegląd

Narzędzia do przetwarzania plików uploadowanych przez użytkownika:
1. **PDF Processor** - ekstrakcja tekstu, tabel, metadanych
2. **DOCX Processor** - parsowanie dokumentów Word
3. **XLSX/CSV Processor** - dane tabelaryczne
4. **Image Analyzer** - OCR, analiza obrazów

---

## 1. PDF PROCESSOR

### 1.1 PDF Extractor

```python
# tools/files/pdf_processor.py

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import io
import re

@dataclass
class ExtractedPDFPage:
    """Wyekstrahowana strona PDF"""
    page_number: int
    text: str
    tables: List[List[List[str]]]  # Lista tabel, każda to lista wierszy
    images: List[Dict]  # image bytes, position, size
    layout: str  # 'single_column', 'multi_column', 'mixed'

@dataclass
class ExtractedPDF:
    """Wyekstrahowany dokument PDF"""
    filename: str
    total_pages: int
    pages: List[ExtractedPDFPage]
    
    # Metadane
    title: Optional[str]
    author: Optional[str]
    subject: Optional[str]
    creation_date: Optional[str]
    
    # Agregowane dane
    full_text: str
    all_tables: List[Dict]  # z page numbers
    
    # Wykryte elementy
    detected_type: str  # 'report', 'invoice', 'contract', 'presentation', 'other'
    detected_entities: Dict  # companies, dates, amounts, etc.


class PDFProcessor:
    """
    Zaawansowany procesor PDF z obsługą różnych typów dokumentów.
    """
    
    def __init__(self, ocr_enabled: bool = True):
        self.ocr_enabled = ocr_enabled
    
    async def process(self, file_path: str) -> ExtractedPDF:
        """
        Przetwórz plik PDF i wyekstrahuj wszystkie dane.
        """
        # 1. Otwórz PDF
        doc = fitz.open(file_path)
        
        # 2. Wyciągnij metadane
        metadata = doc.metadata
        
        # 3. Przetwórz strony
        pages = []
        all_text = []
        all_tables = []
        
        for page_num in range(len(doc)):
            page_data = await self._process_page(doc, page_num, file_path)
            pages.append(page_data)
            all_text.append(page_data.text)
            
            for i, table in enumerate(page_data.tables):
                all_tables.append({
                    'page': page_num + 1,
                    'table_index': i,
                    'data': table
                })
        
        # 4. Złącz tekst
        full_text = "\n\n".join(all_text)
        
        # 5. Wykryj typ dokumentu
        doc_type = self._detect_document_type(full_text, all_tables)
        
        # 6. Wyekstrahuj encje
        entities = self._extract_entities(full_text)
        
        doc.close()
        
        return ExtractedPDF(
            filename=file_path.split('/')[-1],
            total_pages=len(pages),
            pages=pages,
            title=metadata.get('title'),
            author=metadata.get('author'),
            subject=metadata.get('subject'),
            creation_date=metadata.get('creationDate'),
            full_text=full_text,
            all_tables=all_tables,
            detected_type=doc_type,
            detected_entities=entities
        )
    
    async def _process_page(
        self, 
        doc: fitz.Document, 
        page_num: int,
        file_path: str
    ) -> ExtractedPDFPage:
        """Przetwórz pojedynczą stronę"""
        page = doc.load_page(page_num)
        
        # 1. Tekst
        text = page.get_text("text")
        
        # Jeśli tekst jest pusty lub za krótki, spróbuj OCR
        if self.ocr_enabled and len(text.strip()) < 50:
            text = await self._ocr_page(page)
        
        # 2. Tabele (używamy pdfplumber dla lepszej ekstrakcji)
        tables = self._extract_tables_from_page(file_path, page_num)
        
        # 3. Obrazy
        images = self._extract_images_from_page(page)
        
        # 4. Wykryj layout
        layout = self._detect_layout(page)
        
        return ExtractedPDFPage(
            page_number=page_num + 1,
            text=text,
            tables=tables,
            images=images,
            layout=layout
        )
    
    def _extract_tables_from_page(
        self, 
        file_path: str, 
        page_num: int
    ) -> List[List[List[str]]]:
        """Wyekstrahuj tabele używając pdfplumber"""
        tables = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    extracted = page.extract_tables()
                    
                    for table in extracted:
                        # Oczyść dane
                        cleaned = []
                        for row in table:
                            cleaned_row = [
                                cell.strip() if cell else '' 
                                for cell in row
                            ]
                            if any(cleaned_row):  # Pomiń puste wiersze
                                cleaned.append(cleaned_row)
                        
                        if cleaned:
                            tables.append(cleaned)
        except Exception as e:
            print(f"Table extraction error: {e}")
        
        return tables
    
    def _extract_images_from_page(self, page: fitz.Page) -> List[Dict]:
        """Wyekstrahuj obrazy ze strony"""
        images = []
        
        for img_index, img in enumerate(page.get_images()):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                
                images.append({
                    'index': img_index,
                    'width': base_image['width'],
                    'height': base_image['height'],
                    'format': base_image['ext'],
                    'size_bytes': len(base_image['image'])
                })
            except Exception as e:
                print(f"Image extraction error: {e}")
        
        return images
    
    async def _ocr_page(self, page: fitz.Page) -> str:
        """OCR strony jeśli tekst jest nieczytelny"""
        # Renderuj stronę do obrazu
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        
        # Użyj Tesseract lub zewnętrznego API
        try:
            import pytesseract
            from PIL import Image
            
            img = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(img, lang='pol+eng')
            return text
        except ImportError:
            # Fallback - zwróć pusty tekst
            return ""
    
    def _detect_layout(self, page: fitz.Page) -> str:
        """Wykryj layout strony"""
        # Analizuj bloki tekstowe
        blocks = page.get_text("dict")["blocks"]
        
        if not blocks:
            return 'empty'
        
        # Sprawdź czy są kolumny
        x_positions = []
        for block in blocks:
            if block.get("type") == 0:  # text block
                x_positions.append(block["bbox"][0])
        
        if len(set(x_positions)) > 2:
            return 'multi_column'
        elif len(set(x_positions)) == 2:
            return 'two_column'
        else:
            return 'single_column'
    
    def _detect_document_type(
        self, 
        text: str, 
        tables: List[Dict]
    ) -> str:
        """Wykryj typ dokumentu na podstawie zawartości"""
        text_lower = text.lower()
        
        # Faktura
        if any(word in text_lower for word in ['faktura', 'invoice', 'netto', 'brutto', 'vat']):
            if 'nip' in text_lower:
                return 'invoice'
        
        # Umowa
        if any(word in text_lower for word in ['umowa', 'contract', 'strony ustalają', 'przedmiot umowy']):
            return 'contract'
        
        # Sprawozdanie finansowe
        if any(word in text_lower for word in ['sprawozdanie finansowe', 'bilans', 'rachunek zysków i strat']):
            return 'financial_statement'
        
        # Raport
        if any(word in text_lower for word in ['raport', 'report', 'podsumowanie', 'wnioski']):
            return 'report'
        
        # Prezentacja
        if len(tables) > 5 or 'slide' in text_lower:
            return 'presentation'
        
        return 'other'
    
    def _extract_entities(self, text: str) -> Dict:
        """Wyekstrahuj encje z tekstu"""
        entities = {
            'companies': [],
            'nips': [],
            'dates': [],
            'amounts': [],
            'emails': [],
            'phones': []
        }
        
        # NIP
        nip_pattern = r'NIP[:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})'
        for match in re.finditer(nip_pattern, text):
            entities['nips'].append(re.sub(r'[-\s]', '', match.group(1)))
        
        # Daty
        date_patterns = [
            r'\d{1,2}[./]\d{1,2}[./]\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}\s+(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s+\d{4}'
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Kwoty
        amount_pattern = r'(\d{1,3}(?:[\s,]\d{3})*(?:[.,]\d{2})?)\s*(?:PLN|zł|EUR|USD|€|\$)'
        for match in re.finditer(amount_pattern, text):
            entities['amounts'].append(match.group(0))
        
        # Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        entities['emails'] = re.findall(email_pattern, text)
        
        # Telefon
        phone_pattern = r'(?:\+48[\s.-]?)?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}'
        entities['phones'] = re.findall(phone_pattern, text)
        
        return entities
```

---

## 2. DOCX PROCESSOR

### 2.1 Word Document Processor

```python
# tools/files/docx_processor.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import re

@dataclass
class ExtractedDOCX:
    """Wyekstrahowany dokument Word"""
    filename: str
    
    # Treść
    paragraphs: List[Dict]  # text, style, level
    tables: List[List[List[str]]]
    images: List[Dict]
    
    # Struktura
    headings: List[Dict]  # text, level
    sections: List[Dict]  # title, content
    
    # Metadane
    title: Optional[str]
    author: Optional[str]
    created: Optional[str]
    modified: Optional[str]
    
    # Agregowane
    full_text: str
    word_count: int
    
    # Wykryte
    detected_type: str
    detected_entities: Dict


class DOCXProcessor:
    """
    Procesor dokumentów Word.
    """
    
    def process(self, file_path: str) -> ExtractedDOCX:
        """
        Przetwórz dokument DOCX.
        """
        doc = Document(file_path)
        
        # 1. Wyciągnij paragrafy
        paragraphs = []
        headings = []
        all_text = []
        
        for para in doc.paragraphs:
            para_data = {
                'text': para.text,
                'style': para.style.name if para.style else None,
                'level': self._get_heading_level(para)
            }
            paragraphs.append(para_data)
            
            if para.text.strip():
                all_text.append(para.text)
            
            # Headings
            if para_data['level'] > 0:
                headings.append({
                    'text': para.text,
                    'level': para_data['level']
                })
        
        # 2. Wyciągnij tabele
        tables = []
        for table in doc.tables:
            table_data = self._extract_table(table)
            tables.append(table_data)
        
        # 3. Wyciągnij obrazy
        images = self._extract_images(doc)
        
        # 4. Zbuduj sekcje
        sections = self._build_sections(paragraphs, headings)
        
        # 5. Metadane
        core_props = doc.core_properties
        
        # 6. Pełny tekst
        full_text = "\n".join(all_text)
        
        # 7. Wykryj typ i encje
        doc_type = self._detect_type(full_text, headings)
        entities = self._extract_entities(full_text)
        
        return ExtractedDOCX(
            filename=file_path.split('/')[-1],
            paragraphs=paragraphs,
            tables=tables,
            images=images,
            headings=headings,
            sections=sections,
            title=core_props.title,
            author=core_props.author,
            created=str(core_props.created) if core_props.created else None,
            modified=str(core_props.modified) if core_props.modified else None,
            full_text=full_text,
            word_count=len(full_text.split()),
            detected_type=doc_type,
            detected_entities=entities
        )
    
    def _get_heading_level(self, para: Paragraph) -> int:
        """Określ poziom nagłówka"""
        if para.style:
            style_name = para.style.name
            if style_name.startswith('Heading'):
                try:
                    return int(style_name.split()[-1])
                except:
                    pass
            if style_name in ['Title', 'Tytuł']:
                return 0  # Tytuł dokumentu
        return -1  # Nie jest nagłówkiem
    
    def _extract_table(self, table: Table) -> List[List[str]]:
        """Wyekstrahuj dane z tabeli"""
        data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text.strip())
            data.append(row_data)
        return data
    
    def _extract_images(self, doc: Document) -> List[Dict]:
        """Wyekstrahuj informacje o obrazach"""
        images = []
        
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                images.append({
                    'rel_id': rel.rId,
                    'target': rel.target_ref,
                    'type': rel.reltype
                })
        
        return images
    
    def _build_sections(
        self, 
        paragraphs: List[Dict],
        headings: List[Dict]
    ) -> List[Dict]:
        """Zbuduj strukturę sekcji"""
        sections = []
        current_section = None
        
        for para in paragraphs:
            if para['level'] > 0:
                # Nowa sekcja
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'title': para['text'],
                    'level': para['level'],
                    'content': []
                }
            elif current_section and para['text'].strip():
                current_section['content'].append(para['text'])
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _detect_type(self, text: str, headings: List[Dict]) -> str:
        """Wykryj typ dokumentu"""
        text_lower = text.lower()
        heading_texts = ' '.join([h['text'].lower() for h in headings])
        
        # Umowa
        if 'umowa' in text_lower or 'contract' in text_lower:
            return 'contract'
        
        # Oferta
        if 'oferta' in text_lower or 'proposal' in text_lower:
            return 'proposal'
        
        # Raport
        if 'raport' in text_lower or 'report' in text_lower:
            return 'report'
        
        # Specyfikacja
        if 'specyfikacja' in text_lower or 'specification' in text_lower:
            return 'specification'
        
        # Notatka
        if 'notatka' in text_lower or 'note' in text_lower:
            return 'note'
        
        return 'document'
    
    def _extract_entities(self, text: str) -> Dict:
        """Wyekstrahuj encje (reuse z PDF)"""
        # Taki sam kod jak w PDF processor
        entities = {
            'companies': [],
            'nips': [],
            'dates': [],
            'amounts': [],
            'emails': [],
            'phones': []
        }
        
        # NIP
        nip_pattern = r'NIP[:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})'
        for match in re.finditer(nip_pattern, text):
            entities['nips'].append(re.sub(r'[-\s]', '', match.group(1)))
        
        # Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        entities['emails'] = re.findall(email_pattern, text)
        
        return entities
```

---

## 3. SPREADSHEET PROCESSOR

### 3.1 Excel/CSV Processor

```python
# tools/files/spreadsheet_processor.py

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import pandas as pd
import openpyxl
from io import BytesIO

@dataclass
class ExtractedSpreadsheet:
    """Wyekstrahowany arkusz kalkulacyjny"""
    filename: str
    file_type: str  # 'xlsx', 'xls', 'csv'
    
    # Arkusze
    sheets: List[Dict]  # name, data, summary
    
    # Pierwszy arkusz jako DataFrame summary
    columns: List[str]
    row_count: int
    column_count: int
    
    # Statystyki danych
    data_types: Dict[str, str]  # column -> type
    null_counts: Dict[str, int]
    numeric_summaries: Dict[str, Dict]  # min, max, mean, median
    
    # Wykryte wzorce
    detected_structure: str  # 'table', 'pivot', 'report', 'raw_data'
    has_headers: bool
    has_totals_row: bool


class SpreadsheetProcessor:
    """
    Procesor arkuszy kalkulacyjnych (Excel, CSV).
    """
    
    def process(self, file_path: str) -> ExtractedSpreadsheet:
        """
        Przetwórz arkusz kalkulacyjny.
        """
        file_type = file_path.split('.')[-1].lower()
        
        if file_type == 'csv':
            return self._process_csv(file_path)
        else:
            return self._process_excel(file_path)
    
    def _process_excel(self, file_path: str) -> ExtractedSpreadsheet:
        """Przetwórz plik Excel"""
        xl = pd.ExcelFile(file_path)
        
        sheets = []
        main_df = None
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            
            if main_df is None:
                main_df = df
            
            sheet_data = {
                'name': sheet_name,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'preview': df.head(5).to_dict('records'),
                'data': df  # Pełne dane
            }
            sheets.append(sheet_data)
        
        # Analiza głównego arkusza
        columns = list(main_df.columns)
        data_types = {col: str(main_df[col].dtype) for col in columns}
        null_counts = {col: int(main_df[col].isnull().sum()) for col in columns}
        
        # Statystyki numeryczne
        numeric_summaries = {}
        for col in main_df.select_dtypes(include=['number']).columns:
            numeric_summaries[col] = {
                'min': float(main_df[col].min()) if not pd.isna(main_df[col].min()) else None,
                'max': float(main_df[col].max()) if not pd.isna(main_df[col].max()) else None,
                'mean': float(main_df[col].mean()) if not pd.isna(main_df[col].mean()) else None,
                'median': float(main_df[col].median()) if not pd.isna(main_df[col].median()) else None,
                'sum': float(main_df[col].sum()) if not pd.isna(main_df[col].sum()) else None
            }
        
        # Wykryj strukturę
        structure = self._detect_structure(main_df)
        has_headers = self._has_headers(main_df)
        has_totals = self._has_totals_row(main_df)
        
        return ExtractedSpreadsheet(
            filename=file_path.split('/')[-1],
            file_type='xlsx',
            sheets=sheets,
            columns=columns,
            row_count=len(main_df),
            column_count=len(columns),
            data_types=data_types,
            null_counts=null_counts,
            numeric_summaries=numeric_summaries,
            detected_structure=structure,
            has_headers=has_headers,
            has_totals_row=has_totals
        )
    
    def _process_csv(self, file_path: str) -> ExtractedSpreadsheet:
        """Przetwórz plik CSV"""
        # Wykryj encoding i separator
        encoding = self._detect_encoding(file_path)
        separator = self._detect_separator(file_path, encoding)
        
        df = pd.read_csv(file_path, encoding=encoding, sep=separator)
        
        sheets = [{
            'name': 'Sheet1',
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'preview': df.head(5).to_dict('records'),
            'data': df
        }]
        
        columns = list(df.columns)
        data_types = {col: str(df[col].dtype) for col in columns}
        null_counts = {col: int(df[col].isnull().sum()) for col in columns}
        
        numeric_summaries = {}
        for col in df.select_dtypes(include=['number']).columns:
            numeric_summaries[col] = {
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'sum': float(df[col].sum()) if not pd.isna(df[col].sum()) else None
            }
        
        return ExtractedSpreadsheet(
            filename=file_path.split('/')[-1],
            file_type='csv',
            sheets=sheets,
            columns=columns,
            row_count=len(df),
            column_count=len(columns),
            data_types=data_types,
            null_counts=null_counts,
            numeric_summaries=numeric_summaries,
            detected_structure=self._detect_structure(df),
            has_headers=self._has_headers(df),
            has_totals_row=self._has_totals_row(df)
        )
    
    def _detect_encoding(self, file_path: str) -> str:
        """Wykryj encoding pliku"""
        try:
            import chardet
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read(10000))
            return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'
    
    def _detect_separator(self, file_path: str, encoding: str) -> str:
        """Wykryj separator CSV"""
        with open(file_path, 'r', encoding=encoding) as f:
            first_line = f.readline()
        
        separators = [',', ';', '\t', '|']
        counts = {sep: first_line.count(sep) for sep in separators}
        return max(counts, key=counts.get)
    
    def _detect_structure(self, df: pd.DataFrame) -> str:
        """Wykryj strukturę danych"""
        # Pivot table - ma zagnieżdżone nagłówki lub dużo pustych komórek
        null_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if null_ratio > 0.3:
            return 'pivot'
        
        # Report - ma merged cells lub nieregularną strukturę
        # (trudne do wykrycia w pandas)
        
        # Raw data - regularna tabela
        return 'table'
    
    def _has_headers(self, df: pd.DataFrame) -> bool:
        """Sprawdź czy pierwszy wiersz to nagłówki"""
        # Jeśli kolumny są typu "Unnamed: X", prawdopodobnie brak nagłówków
        unnamed_count = sum(1 for col in df.columns if 'Unnamed' in str(col))
        return unnamed_count < len(df.columns) / 2
    
    def _has_totals_row(self, df: pd.DataFrame) -> bool:
        """Sprawdź czy ostatni wiersz to podsumowanie"""
        if len(df) < 2:
            return False
        
        last_row = df.iloc[-1]
        
        # Sprawdź czy zawiera słowa kluczowe
        for val in last_row.values:
            if isinstance(val, str):
                if any(word in val.lower() for word in ['suma', 'total', 'razem', 'ogółem']):
                    return True
        
        return False
    
    def to_summary_text(self, extracted: ExtractedSpreadsheet) -> str:
        """Konwertuj na tekstowe podsumowanie dla LLM"""
        lines = [
            f"Plik: {extracted.filename}",
            f"Typ: {extracted.file_type}",
            f"Wiersze: {extracted.row_count}, Kolumny: {extracted.column_count}",
            f"Struktura: {extracted.detected_structure}",
            "",
            "Kolumny:"
        ]
        
        for col in extracted.columns:
            dtype = extracted.data_types.get(col, 'unknown')
            nulls = extracted.null_counts.get(col, 0)
            lines.append(f"  - {col} ({dtype}, {nulls} pustych)")
        
        if extracted.numeric_summaries:
            lines.append("")
            lines.append("Statystyki numeryczne:")
            for col, stats in extracted.numeric_summaries.items():
                lines.append(f"  {col}: min={stats['min']}, max={stats['max']}, mean={stats['mean']:.2f}")
        
        return "\n".join(lines)
```

---

## 4. IMAGE ANALYZER

### 4.1 Image Analysis

```python
# tools/files/image_analyzer.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from PIL import Image
import io

@dataclass
class AnalyzedImage:
    """Przeanalizowany obraz"""
    filename: str
    format: str
    width: int
    height: int
    mode: str  # RGB, RGBA, L, etc.
    file_size: int
    
    # OCR
    extracted_text: Optional[str]
    
    # AI analysis
    description: Optional[str]
    detected_objects: List[str]
    detected_text_regions: List[Dict]
    
    # Dla dokumentów
    is_document: bool
    document_type: Optional[str]  # 'invoice', 'receipt', 'business_card', 'screenshot'


class ImageAnalyzer:
    """
    Analizator obrazów z OCR i AI vision.
    """
    
    def __init__(self, anthropic_client=None, tesseract_enabled: bool = True):
        self.anthropic_client = anthropic_client
        self.tesseract_enabled = tesseract_enabled
    
    async def analyze(self, file_path: str) -> AnalyzedImage:
        """
        Przeanalizuj obraz.
        """
        # 1. Podstawowe info
        img = Image.open(file_path)
        
        with open(file_path, 'rb') as f:
            file_size = len(f.read())
        
        # 2. OCR
        extracted_text = None
        if self.tesseract_enabled:
            extracted_text = self._ocr(img)
        
        # 3. AI Vision (jeśli dostępne)
        description = None
        detected_objects = []
        
        if self.anthropic_client:
            vision_result = await self._analyze_with_vision(file_path)
            description = vision_result.get('description')
            detected_objects = vision_result.get('objects', [])
        
        # 4. Wykryj typ dokumentu
        is_document, doc_type = self._detect_document_type(img, extracted_text)
        
        return AnalyzedImage(
            filename=file_path.split('/')[-1],
            format=img.format or 'unknown',
            width=img.width,
            height=img.height,
            mode=img.mode,
            file_size=file_size,
            extracted_text=extracted_text,
            description=description,
            detected_objects=detected_objects,
            detected_text_regions=[],
            is_document=is_document,
            document_type=doc_type
        )
    
    def _ocr(self, img: Image.Image) -> str:
        """Wykonaj OCR na obrazie"""
        try:
            import pytesseract
            text = pytesseract.image_to_string(img, lang='pol+eng')
            return text.strip()
        except ImportError:
            return None
        except Exception as e:
            print(f"OCR error: {e}")
            return None
    
    async def _analyze_with_vision(self, file_path: str) -> Dict:
        """Analizuj obraz używając Claude Vision"""
        if not self.anthropic_client:
            return {}
        
        # Załaduj obraz jako base64
        import base64
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Określ media type
        ext = file_path.split('.')[-1].lower()
        media_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_types.get(ext, 'image/jpeg')
        
        # Wywołaj Claude Vision
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": "Describe this image briefly. List any objects, text, or notable elements you can see. If it's a document, identify its type."
                            }
                        ]
                    }
                ]
            )
            
            return {
                'description': response.content[0].text,
                'objects': []  # Można parsować z odpowiedzi
            }
        except Exception as e:
            print(f"Vision API error: {e}")
            return {}
    
    def _detect_document_type(
        self, 
        img: Image.Image, 
        text: Optional[str]
    ) -> tuple[bool, Optional[str]]:
        """Wykryj czy obraz to dokument i jakiego typu"""
        # Proporcje typowe dla dokumentów
        aspect_ratio = img.width / img.height
        is_portrait = 0.5 < aspect_ratio < 0.9
        is_landscape_doc = 1.1 < aspect_ratio < 1.6
        
        if not (is_portrait or is_landscape_doc):
            # Prawdopodobnie nie dokument
            if text and len(text) < 50:
                return False, None
        
        if not text:
            return is_portrait, 'document'
        
        text_lower = text.lower()
        
        # Faktura
        if any(word in text_lower for word in ['faktura', 'invoice', 'vat', 'nip']):
            return True, 'invoice'
        
        # Paragon
        if any(word in text_lower for word in ['paragon', 'receipt', 'fiskalny']):
            return True, 'receipt'
        
        # Wizytówka
        if img.width < 1000 and img.height < 600:
            if '@' in text or 'tel' in text_lower:
                return True, 'business_card'
        
        # Screenshot
        if any(word in text_lower for word in ['chrome', 'firefox', 'safari', 'http']):
            return True, 'screenshot'
        
        return True, 'document'
```

---

## 5. UNIFIED FILE PROCESSOR

```python
# tools/files/unified_processor.py

from dataclasses import dataclass
from typing import Union, Optional
from pathlib import Path

from .pdf_processor import PDFProcessor, ExtractedPDF
from .docx_processor import DOCXProcessor, ExtractedDOCX
from .spreadsheet_processor import SpreadsheetProcessor, ExtractedSpreadsheet
from .image_analyzer import ImageAnalyzer, AnalyzedImage

@dataclass
class ProcessedFile:
    """Zunifikowany wynik przetwarzania pliku"""
    filename: str
    file_type: str
    file_size: int
    
    # Wyekstrahowane dane (jeden z typów)
    pdf_data: Optional[ExtractedPDF] = None
    docx_data: Optional[ExtractedDOCX] = None
    spreadsheet_data: Optional[ExtractedSpreadsheet] = None
    image_data: Optional[AnalyzedImage] = None
    
    # Zunifikowane pole tekstowe
    text_content: str = ""
    
    # Podsumowanie dla LLM
    summary: str = ""
    
    # Status
    success: bool = True
    error: Optional[str] = None


class UnifiedFileProcessor:
    """
    Zunifikowany procesor plików - automatycznie wykrywa typ i przetwarza.
    """
    
    SUPPORTED_TYPES = {
        'pdf': ['pdf'],
        'docx': ['docx', 'doc'],
        'spreadsheet': ['xlsx', 'xls', 'csv', 'tsv'],
        'image': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp']
    }
    
    def __init__(self, anthropic_client=None):
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        self.spreadsheet_processor = SpreadsheetProcessor()
        self.image_analyzer = ImageAnalyzer(anthropic_client=anthropic_client)
    
    async def process(self, file_path: str) -> ProcessedFile:
        """
        Przetwórz plik dowolnego obsługiwanego typu.
        """
        path = Path(file_path)
        extension = path.suffix.lower().lstrip('.')
        file_size = path.stat().st_size
        
        # Określ typ
        file_type = self._detect_type(extension)
        
        if not file_type:
            return ProcessedFile(
                filename=path.name,
                file_type='unknown',
                file_size=file_size,
                success=False,
                error=f"Unsupported file type: {extension}"
            )
        
        try:
            if file_type == 'pdf':
                data = await self.pdf_processor.process(file_path)
                return ProcessedFile(
                    filename=path.name,
                    file_type='pdf',
                    file_size=file_size,
                    pdf_data=data,
                    text_content=data.full_text,
                    summary=self._summarize_pdf(data)
                )
            
            elif file_type == 'docx':
                data = self.docx_processor.process(file_path)
                return ProcessedFile(
                    filename=path.name,
                    file_type='docx',
                    file_size=file_size,
                    docx_data=data,
                    text_content=data.full_text,
                    summary=self._summarize_docx(data)
                )
            
            elif file_type == 'spreadsheet':
                data = self.spreadsheet_processor.process(file_path)
                return ProcessedFile(
                    filename=path.name,
                    file_type='spreadsheet',
                    file_size=file_size,
                    spreadsheet_data=data,
                    text_content=self.spreadsheet_processor.to_summary_text(data),
                    summary=self._summarize_spreadsheet(data)
                )
            
            elif file_type == 'image':
                data = await self.image_analyzer.analyze(file_path)
                return ProcessedFile(
                    filename=path.name,
                    file_type='image',
                    file_size=file_size,
                    image_data=data,
                    text_content=data.extracted_text or '',
                    summary=self._summarize_image(data)
                )
        
        except Exception as e:
            return ProcessedFile(
                filename=path.name,
                file_type=file_type,
                file_size=file_size,
                success=False,
                error=str(e)
            )
    
    def _detect_type(self, extension: str) -> Optional[str]:
        """Wykryj typ pliku na podstawie rozszerzenia"""
        for file_type, extensions in self.SUPPORTED_TYPES.items():
            if extension in extensions:
                return file_type
        return None
    
    def _summarize_pdf(self, data: ExtractedPDF) -> str:
        """Podsumowanie PDF dla LLM"""
        return f"""PDF Document: {data.filename}
Pages: {data.total_pages}
Type: {data.detected_type}
Tables: {len(data.all_tables)}
Title: {data.title or 'N/A'}
Entities found: NIPs: {len(data.detected_entities.get('nips', []))}, 
Emails: {len(data.detected_entities.get('emails', []))},
Amounts: {len(data.detected_entities.get('amounts', []))}"""
    
    def _summarize_docx(self, data: ExtractedDOCX) -> str:
        """Podsumowanie DOCX dla LLM"""
        return f"""Word Document: {data.filename}
Type: {data.detected_type}
Sections: {len(data.sections)}
Tables: {len(data.tables)}
Words: {data.word_count}
Author: {data.author or 'N/A'}"""
    
    def _summarize_spreadsheet(self, data: ExtractedSpreadsheet) -> str:
        """Podsumowanie arkusza dla LLM"""
        return f"""Spreadsheet: {data.filename}
Sheets: {len(data.sheets)}
Main sheet: {data.row_count} rows x {data.column_count} columns
Structure: {data.detected_structure}
Columns: {', '.join(data.columns[:10])}{'...' if len(data.columns) > 10 else ''}"""
    
    def _summarize_image(self, data: AnalyzedImage) -> str:
        """Podsumowanie obrazu dla LLM"""
        return f"""Image: {data.filename}
Size: {data.width}x{data.height}
Format: {data.format}
Is document: {data.is_document}
Document type: {data.document_type or 'N/A'}
Has text: {'Yes' if data.extracted_text else 'No'}"""
```

---

*Następny dokument: 15_CONFIG_ROUTING.yaml*
