'use client';

export default function TestTableScroll() {
  const companies = [
    {
      id: 1,
      name: 'TechSoft Sp. z o.o.',
      nip: '1234567890',
      city: 'Warszawa',
      revenue: '15,000,000',
      employees: 250,
      industry: 'IT Services',
      founded: '2010',
      status: 'Active',
      website: 'www.techsoft.pl',
    },
    {
      id: 2,
      name: 'BuildMaster Polska',
      nip: '0987654321',
      city: 'Kraków',
      revenue: '45,000,000',
      employees: 480,
      industry: 'Construction',
      founded: '2005',
      status: 'Active',
      website: 'www.buildmaster.pl',
    },
    {
      id: 3,
      name: 'FoodDistro Group',
      nip: '5555666777',
      city: 'Poznań',
      revenue: '28,500,000',
      employees: 320,
      industry: 'Food Distribution',
      founded: '2012',
      status: 'Active',
      website: 'www.fooddistro.pl',
    },
    {
      id: 4,
      name: 'AutoParts International',
      nip: '1112223334',
      city: 'Wrocław',
      revenue: '62,000,000',
      employees: 550,
      industry: 'Automotive',
      founded: '2001',
      status: 'Active',
      website: 'www.autoparts.pl',
    },
    {
      id: 5,
      name: 'MediCare Solutions',
      nip: '9998887776',
      city: 'Gdańsk',
      revenue: '18,200,000',
      employees: 180,
      industry: 'Healthcare',
      founded: '2015',
      status: 'Active',
      website: 'www.medicare.pl',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-bold mb-4">Test: Table Horizontal Scroll on Mobile</h1>
          <p className="text-slate-600 mb-6">
            This table should scroll horizontally on narrow viewports (375px). Test by resizing your browser or using mobile device.
          </p>

          {/* Table container with horizontal scroll */}
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Company Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    NIP
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    City
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Revenue (PLN)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Employees
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Industry
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Founded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider whitespace-nowrap">
                    Website
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {companies.map((company) => (
                  <tr key={company.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {company.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                      {company.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {company.nip}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {company.city}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {company.revenue}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {company.employees}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {company.industry}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {company.founded}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {company.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 hover:text-blue-800">
                      {company.website}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Scroll indicator hint */}
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>✓ Scroll indicator:</strong> On mobile, you should see a scrollbar at the bottom of the table indicating that more columns are available by scrolling horizontally.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
