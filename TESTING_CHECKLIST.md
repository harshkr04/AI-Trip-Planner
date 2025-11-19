# Testing Checklist

## 1. Flight Page - Advanced Options
- [ ] Navigate to `/flights`
- [ ] Verify basic search (origin, destination, date) works
- [ ] Click "Advanced Options" section to expand
- [ ] Verify grid layout: 3 columns on desktop, 2 on tablet, 1 on mobile
- [ ] Test all 6 fields:
  - [ ] Cabin Class dropdown (Economy, Premium, Business, First)
  - [ ] Currency dropdown (INR, USD, EUR)
  - [ ] Trip Type dropdown (One-way, Round-trip)
  - [ ] Stops dropdown (Any, Non-stop, 1 Stop, 2+ Stops)
  - [ ] Max Price number input
  - [ ] Airlines text input (comma-separated)
- [ ] Verify inputs are 44px height, rounded corners (10px), consistent spacing
- [ ] Submit search with advanced options and verify results

## 2. Trip Builder / Home Page
- [ ] Navigate to home page (`/`)
- [ ] Verify hero section loads immediately (no blank screen)
- [ ] Verify main prompt input:
  - [ ] Height ~56px
  - [ ] Font size 18px
  - [ ] Occupies ~65-70% of row width
  - [ ] Placeholder text is visible (#7b7b7b color)
- [ ] Verify date inputs:
  - [ ] Width ~12-14rem each
  - [ ] Height ~44px
  - [ ] Font size 16px
  - [ ] Datepicker opens below input
  - [ ] Datepicker day cells are 34-40px square
  - [ ] Current day has rounded pill highlight with accent color
  - [ ] Datepicker never clips screen edge (smart positioning)
- [ ] Verify Build Plan button:
  - [ ] Vertically aligned with inputs
  - [ ] Height ~48-52px
  - [ ] Rounded corners
- [ ] Test date validation:
  - [ ] Try end date before start date → should show error
  - [ ] Try submitting without dates → should show error
- [ ] Test Enter key submission (form should submit)

## 3. Sign-in Modal
- [ ] Click sign-in button (profile menu)
- [ ] Verify modal:
  - [ ] Centered in viewport
  - [ ] Max width ~600-700px on desktop
  - [ ] Soft backdrop blur effect
  - [ ] Smooth open animation (scale + fade)
  - [ ] High z-index (10000) - never escapes layout
  - [ ] Drop shadow visible
- [ ] Test close:
  - [ ] Click X button → closes smoothly
  - [ ] Click outside overlay → closes
  - [ ] Press ESC → closes
- [ ] Test form:
  - [ ] Switch between Sign in / Create account
  - [ ] All inputs have proper focus states
  - [ ] Submit works

## 4. Hotels Page
- [ ] Navigate to `/hotels`
- [ ] Enter destination, check-in, check-out dates
- [ ] Verify loading skeleton appears while fetching
- [ ] Verify results display (even if API fails, mock data should show)
- [ ] Test date validation:
  - [ ] Check-out before check-in → error message
- [ ] Verify responsive layout on mobile

## 5. Location Details (New Endpoint)
- [ ] Test endpoint: `GET /api/location/details?location=Goa`
- [ ] Verify response includes:
  - [ ] `summary` (text)
  - [ ] `youtube_videos` (array with title, videoId, thumbnail)
  - [ ] `activities` (array with title, type, duration)
  - [ ] `news_articles` (array)
- [ ] Test with missing API keys → should return mock data
- [ ] Test with invalid location → should still return mock data

## 6. History Delete
- [ ] Create a few chat sessions
- [ ] Click delete on a chat item
- [ ] Confirm deletion in modal
- [ ] Verify:
  - [ ] Toast appears at bottom: "Chat deleted"
  - [ ] Toast has "Undo" button
  - [ ] Chat is removed from list
- [ ] Test undo:
  - [ ] Click "Undo" → chat should reappear
  - [ ] Verify it's restored to correct position
- [ ] Test without undo:
  - [ ] Delete another chat
  - [ ] Wait 5 seconds → toast auto-closes
  - [ ] Chat remains deleted
- [ ] Verify DELETE `/api/history/{id}` endpoint works
- [ ] Check browser console for errors

## 7. Travel News / Blogs
- [ ] Navigate to `/news`
- [ ] Verify loading skeleton appears while fetching
- [ ] Search for a topic
- [ ] Verify articles display
- [ ] Test with missing API key → should show mock articles
- [ ] Verify responsive layout

## 8. Responsive Behavior
- [ ] Test on mobile (< 640px):
  - [ ] Advanced options grid stacks to 1 column
  - [ ] Trip builder inputs stack vertically
  - [ ] Prompt input full width first
  - [ ] Date inputs in separate rows
  - [ ] Toast adapts to screen width
- [ ] Test on tablet (640-960px):
  - [ ] Advanced options: 2 columns
  - [ ] Layout adapts smoothly
- [ ] Test on desktop (> 960px):
  - [ ] All layouts use full space
  - [ ] 3-column grid for advanced options

## 9. General QA
- [ ] No console errors
- [ ] No CORS errors
- [ ] All API calls handle errors gracefully
- [ ] Loading states show skeletons (not blank screens)
- [ ] Date validation prevents invalid submissions
- [ ] All animations are smooth (160ms transitions)
- [ ] Focus states visible on all inputs
- [ ] Keyboard navigation works (Tab, Enter, ESC)

## 10. Backend Endpoints
- [ ] `POST /api/hotels` - Returns mock data if API fails
- [ ] `GET /api/location/details?location=...` - Returns aggregated data
- [ ] `DELETE /api/history/{id}` - Deletes session/history item
- [ ] `DELETE /api/sessions/{id}` - Still works (backward compatible)

---

## Quick Test Commands

```bash
# Start backend
cd backend
uvicorn main:app --reload

# Start frontend
cd frontend
npm start

# Test endpoints
curl http://localhost:8000/api/hotels -X POST -H "Content-Type: application/json" -d '{"destination":"Goa","start_date":"2025-12-01","end_date":"2025-12-05"}'
curl http://localhost:8000/api/location/details?location=Goa
curl http://localhost:8000/api/history/{session_id} -X DELETE
```

