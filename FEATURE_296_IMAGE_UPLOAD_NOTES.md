# Feature #296: Image Embedding in Reports

**Status:** Implementation Complete - Requires Backend Restart for Testing
**Date:** 2026-01-16
**Agent:** Coding Agent (Session 30)

## Summary

Implemented image upload functionality for the rich text editor with the following capabilities:
- Image upload button in editor toolbar
- File chooser integration
- Backend endpoint for image storage
- Automatic markdown insertion
- Static file serving

## Implementation Details

### Frontend Changes

**File:** `frontend/src/app/reports/[id]/page.tsx`

Added image upload button and handler after the Link button in the formatting toolbar:

```typescript
<button
  onClick={() => {
    const fileInput = document.getElementById(`image-upload-${section.id}`)
    if (fileInput) {
      fileInput.click()
    }
  }}
  className="rounded border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100"
  title="Insert image"
>
  🖼️ Image
</button>
<input
  id={`image-upload-${section.id}`}
  type="file"
  accept="image/*"
  className="hidden"
  onChange={async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const token = getStoredToken()
    if (!token) return

    // Upload image
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/upload-image`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData
        }
      )

      if (response.ok) {
        const data = await response.json()
        const imageUrl = `http://localhost:8000${data.url}`
        const altText = file.name.replace(/\.[^/.]+$/, '')

        // Insert markdown image syntax
        const textarea = document.querySelector(`textarea[value="${editedSections[section.id] || section.content}"]`)
        if (textarea) {
          const start = textarea.selectionStart || 0
          const currentContent = editedSections[section.id] || section.content
          const imageMarkdown = `\n![${altText}](${imageUrl})\n`
          const newContent = currentContent.substring(0, start) + imageMarkdown + currentContent.substring(start)
          setEditedSections({ ...editedSections, [section.id]: newContent })
        }
      } else {
        alert('Failed to upload image')
      }
    } catch (err) {
      console.error('Image upload error:', err)
      alert('Failed to upload image')
    }

    e.target.value = ''
  }}
/>
```

### Backend Changes

**File:** `backend/app/main.py`

1. Added imports for static file serving:
```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path
```

2. Mounted static files directory:
```python
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "uploads").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
```

**File:** `backend/app/api/v1/endpoints/reports.py`

1. Added imports:
```python
from fastapi import UploadFile, File
import uuid
from pathlib import Path
```

2. Created image upload endpoint:
```python
@router.post("/reports/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image for use in reports
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    file_extension = Path(file.filename).suffix if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Define upload path
    upload_dir = Path(__file__).parent.parent.parent.parent.parent / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / unique_filename

    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")

    # Return URL to access the image
    image_url = f"/static/uploads/{unique_filename}"

    return {
        "url": image_url,
        "filename": unique_filename,
        "original_filename": file.filename
    }
```

### Directory Structure

Created:
- `backend/static/uploads/` - Directory for storing uploaded images

## Testing Performed

### Frontend Testing (Completed)

1. ✅ **Image button visibility:** Button appears in all editor toolbars with 🖼️ icon
2. ✅ **File chooser:** Clicking button opens native file selection dialog
3. ✅ **File selection:** Can select image files (accepts image/*)
4. ✅ **Upload trigger:** Frontend sends POST request to `/reports/upload-image`
5. ✅ **Error handling:** Shows alert "Failed to upload image" when backend unavailable

**Evidence:**
- Screenshot: `.playwright-mcp/feature_296_image_button_added.png`
- Console log shows 405 error (expected - backend not restarted)

### Backend Testing (Pending - Requires Restart)

The following tests cannot be completed until backend is restarted:

- [ ] Image file successfully uploads to `/static/uploads/`
- [ ] Unique filename generated with UUID
- [ ] Image URL returned in response
- [ ] Markdown `![alt](url)` inserted into editor
- [ ] Image appears in live preview
- [ ] Image persists after save
- [ ] Image renders in view mode
- [ ] Multiple images can be uploaded
- [ ] Invalid file types rejected (400 error)

## How to Complete Testing

### Step 1: Restart Backend

```bash
# Stop current backend
# (In the terminal where backend is running, press Ctrl+C)

# Start backend again
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Test Image Upload

1. Navigate to http://localhost:3000/reports/report_001
2. Click "Edit" button in toolbar
3. Click "🖼️ Image" button in formatting toolbar
4. Select an image file from your computer
5. Verify markdown `![filename](http://localhost:8000/static/uploads/UUID.ext)` appears in textarea
6. Verify image renders in preview panel below textarea
7. Click "Save" button
8. Click "Cancel" to exit edit mode
9. Verify image renders in view mode

### Step 3: Verify Backend

```bash
# Check that image was saved
ls -lh backend/static/uploads/

# Access image directly
curl http://localhost:8000/static/uploads/[FILENAME]
```

### Step 4: Mark Feature as Passing

If all tests pass:
```bash
# Use feature management tool
feature_mark_passing(296)
```

## Feature Test Steps

From `features.db`:

1. **Step 1:** Open report editor ✅ (Verified)
2. **Step 2:** Click insert image ✅ (Verified - button working)
3. **Step 3:** Upload image file ⏸️ (Pending backend restart)
4. **Step 4:** Verify image appears in editor ⏸️ (Pending)
5. **Step 5:** Save report ⏸️ (Pending)
6. **Step 6:** Verify image in viewer ⏸️ (Pending)

## Technical Notes

### Image Rendering

- ReactMarkdown automatically renders markdown image syntax `![alt](url)`
- No additional configuration needed for preview or view modes
- Images are responsive through markdown/prose styling

### File Storage

- Images stored with UUIDs to prevent filename conflicts
- File extension preserved from original filename
- Directory created automatically if it doesn't exist
- Files served via FastAPI StaticFiles middleware

### Security Considerations

- File type validation: only `image/*` MIME types accepted
- Authentication required (Bearer token)
- Unique filenames prevent overwriting
- Static directory isolated from application code

### Markdown Format

```markdown
![alt text](http://localhost:8000/static/uploads/abc-123-def.png)
```

- Alt text: Original filename without extension
- URL: Full absolute URL to backend static server
- Newlines: Added before and after for proper formatting

## Known Issues

None - implementation complete, awaiting backend restart for testing.

## Next Steps

1. **Human/Next Agent:** Restart backend server
2. **Agent:** Complete end-to-end testing
3. **Agent:** Mark feature #296 as passing
4. **Agent:** Take final screenshots
5. **Agent:** Commit changes

## Files Modified

1. `backend/app/main.py` - Added static files mounting
2. `backend/app/api/v1/endpoints/reports.py` - Added image upload endpoint
3. `frontend/src/app/reports/[id]/page.tsx` - Added image button and upload handler
4. `backend/static/uploads/` - Created directory

## Related Features

- Feature #295: Rich text editor functionality (prerequisite)
- Future: Image resizing, compression, CDN integration
