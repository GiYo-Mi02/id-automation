# Frontend API Integration Guide

## Authentication Setup

### 1. **Install Dependencies**
```bash
cd UI
pip install psutil  # For backend system stats
```

### 2. **Configure API Key**
The API key in `UI/.env` must match the backend's API key in root `.env`:

**Backend (.env):**
```
API_KEY=hE_wZo2nC99rrJoz2teepVl22MX3T9vsOnZgZGgKtTU
```

**Frontend (UI/.env):**
```
VITE_API_KEY=hE_wZo2nC99rrJoz2teepVl22MX3T9vsOnZgZGgKtTU
```

### 3. **Use the API Client**

Replace all `fetch()` calls with the new `api` utility:

**Before:**
```javascript
// ❌ Old way - no authentication
const response = await fetch('/api/students');
const students = await response.json();
```

**After:**
```javascript
// ✅ New way - automatic authentication
import api from '@/utils/api';

const students = await api.get('/students');
```

---

## API Client Methods

```javascript
import api from '@/utils/api';

// GET request
const students = await api.get('/students');
const student = await api.get(`/students/${id}`);

// POST request
const newStudent = await api.post('/students', {
  id_number: '2024-123',
  full_name: 'John Doe',
});

// PUT request (update)
const updated = await api.put(`/students/${id}`, {
  full_name: 'Jane Doe',
});

// DELETE request
await api.delete(`/students/${id}`);

// File upload (FormData)
const formData = new FormData();
formData.append('file', file);
const preview = await api.post('/students/import/preview', formData);
```

---

## Error Handling

```javascript
import api from '@/utils/api';

try {
  const students = await api.get('/students');
} catch (error) {
  if (error.status === 401) {
    console.error('Unauthorized - check API key');
  } else if (error.status === 404) {
    console.error('Not found');
  } else {
    console.error('Error:', error.message);
  }
}
```

---

## Migration Checklist

### Find and Replace in all React components:

1. **Import the API client:**
```javascript
import api from '@/utils/api';
```

2. **Replace fetch calls:**

**Students:**
```javascript
// Before
fetch('/api/students')
// After
api.get('/students')
```

**Settings:**
```javascript
// Before
fetch('/api/settings')
// After
api.get('/settings')
```

**History:**
```javascript
// Before
fetch('/api/history?limit=20')
// After
api.get('/history?limit=20')
```

**Stats:**
```javascript
// Before
fetch('/api/stats')
// After
api.get('/system/stats')  // Note: endpoint changed
```

**Update Student:**
```javascript
// Before
fetch(`/api/students/${id}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
// After
api.put(`/students/${id}`, data)
```

---

## New Endpoints

### System Stats
```javascript
const stats = await api.get('/system/stats');
// Returns: { system: {...}, database: {...}, students: {...} }
```

### CSV Import Preview
```javascript
const formData = new FormData();
formData.append('file', csvFile);

const preview = await api.post('/students/import/preview', formData);
// Returns: { total_rows, headers, preview_data, valid, ... }
```

### CSV Import Execute
```javascript
const formData = new FormData();
formData.append('file', csvFile);

const result = await api.post('/students/import', formData);
// Returns: { status, imported, total, errors }
```

---

## Files to Update

Search for `fetch('/api` in these files and replace with `api.get/post/put/delete`:

- `src/hooks/useStudents.js`
- `src/hooks/useTemplates.js`
- `src/contexts/SettingsContext.jsx`
- `src/components/dashboard/StudentTable.jsx`
- `src/components/dashboard/EditStudentModal.jsx`
- `src/components/settings/ImportDataSection.jsx`
- Any custom hooks or components making API calls

---

## Restart Required

After adding `.env` file to `UI/`, restart the Vite dev server:

```bash
cd UI
npm run dev
```

The API key will now be included in all requests automatically.
