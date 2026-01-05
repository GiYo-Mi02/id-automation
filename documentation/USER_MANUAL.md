# ID Card System — User Manual

## For Capture Station Operators

This manual explains how to use the ID card capture system. No technical knowledge required.

---

## Getting Started

### 1. Open the Capture Station

In your web browser, go to: `http://localhost:8000`

You will see the Capture Station interface with:
- Live camera feed in the center
- Student selection box on the bottom
- Recent history on the right

---

## Capturing an ID Card

### Step 1: Select Camera

If you have multiple cameras, select the correct one from the "Camera" dropdown.

### Step 2: Choose Student

You have two options:

#### Option A: Database Mode (Default)
- Type the student's ID number or name in the search box
- Select the student from the dropdown list
- Their information will be loaded automatically

#### Option B: Manual Mode
- Click the "Manual" tab
- Enter the required information:
  - **ID Number** (required)
  - **Full Name** (required)
  - Grade Level (optional)
  - Section (optional)
  - Guardian Name (optional)
  - Address (optional)
  - Contact Number (optional)

### Step 3: Position the Student

Guide the student to:
- Stand 2-3 feet from the camera
- Look directly at the camera
- Keep their head straight
- Make sure lighting is even on their face

A guide overlay shows where the photo and body should be positioned.

### Step 4: Capture

- Click the **CAPTURE** button
- The system will process the photo (this takes 5-15 seconds)
- A preview will appear showing the front and back of the ID card

### Step 5: Review

- Check the photo quality
- Check that all text is correct and readable
- If there's a problem, close the preview and capture again

---

## Viewing Previous IDs

The "Recent History" panel on the right shows:
- Student ID numbers
- Thumbnail of the front card
- Click any item to view the full ID cards

---

## Common Issues

### "Please select a student" error

You didn't select a student or enter manual information. Make sure:
- Database mode: A student is selected from the dropdown
- Manual mode: ID Number and Full Name are filled in

### Camera shows "black screen"

- Check that your camera is connected
- Check browser permissions (click the camera icon in the address bar)
- Try selecting a different camera from the dropdown

### "PROCESSING..." doesn't finish

The system may be:
- Downloading AI models on first run (can take 2-3 minutes)
- Processing a very large photo
- Contact your IT administrator if it takes longer than 5 minutes

### Photo quality is poor

- Improve lighting (bright, even, no shadows)
- Clean the camera lens
- Ask the student to stand still
- Avoid busy backgrounds

### Text is cut off or misaligned

- This requires layout adjustment by an administrator
- Use the Admin Dashboard to edit the student's information
- Click "Save & Regenerate" to create a new card

---

## Tips for Best Results

### Lighting
- Use natural light or bright indoor lighting
- Avoid backlighting (windows behind the student)
- Avoid harsh shadows on the face

### Positioning
- Use the guide overlay to align the student
- Keep the student centered in the frame
- Make sure the entire head and shoulders are visible

### Clothing
- Solid colors work best
- Avoid busy patterns or text on shirts
- School uniform is ideal

### Expression
- Neutral expression
- Eyes open
- Mouth closed
- Looking directly at camera

---

## When to Use Manual Mode

Use Manual Mode when:
- The student is not in the database yet
- You need to create a temporary ID
- The database information is outdated and you need to override it

**Note**: Manual mode information is temporary and does not update the main database.

---

## Need Help?

Contact your IT administrator or system manager if:
- The capture button doesn't work
- Error messages appear
- The camera won't activate
- The quality of generated IDs is consistently poor
