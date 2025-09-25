# Thanks to github user EMZ

## Custom Instructions for Redmine API Usage

## 🚀 IMPORTANT: Full API Access Available
**You have COMPLETE read-write access to the Redmine API!** You can create, update, and delete all resources including issues, projects, users, versions, time entries, and more. Don't limit yourself to read-only operations.

### API Capabilities Summary
- ✅ **Issues**: Create, read, update, delete, manage watchers, relations
- ✅ **Projects**: Create, read, update, delete, archive/unarchive
- ✅ **Versions**: Create, read, update, delete (see Version Management section)
- ✅ **Users**: Create, read, update, delete
- ✅ **Time Entries**: Create, read, update, delete
- ✅ **Project Memberships**: Create, read, update, delete
- ✅ **File Uploads/Downloads**: Upload attachments, download files
- ✅ **News**: Create, read, update, delete
- ✅ **Issue Relations**: Create, read, update, delete

### Useful Tips
- When creating issues, always check the project ID first
- For date parameters, use ISO format: YYYY-MM-DD
- Status IDs: 1=New, 2=In Progress, 3=Resolved, 5=Closed
- Priority IDs: 1=Low, 2=Normal, 3=High, 4=Urgent, 5=Immediate

### Common Query Parameters
- offset: Pagination offset (default: 0)
- limit: Number of items to return (default: 25, max: 100)
- sort: Field to sort by (e.g., 'id:desc', 'priority:asc')

### Example Queries
- Get all open issues: `/issues.json?status_id=open`
- Get high priority issues: `/issues.json?priority_id=>=3`
- Find issues by text: `/issues.json?subject=~search_term`
- Get issues assigned to me: `/issues.json?assigned_to_id=me`

### Time Entry Format
- hours: Decimal number of hours (e.g., 1.5)
- activity_id: Activity type ID
- comments: Optional description of work done

### Issue Creation Fields
- project_id: (required) ID or identifier of the project
- subject: (required) Issue title
- description: Detailed description, supports Markdown
- priority_id: Issue priority (1-5)
- assigned_to_id: User ID to assign the issue to
- parent_issue_id: ID of parent issue for subtasks
- start_date/due_date: Format YYYY-MM-DD
- estimated_hours: Estimated time in decimal hours

### Version Management (Full CRUD Support)
**✅ You CAN create, update, and delete versions!**

#### Creating a Version
Use POST to `/projects/{project_id}/versions.json`:
```json
{
  "version": {
    "name": "Version 1.0.0",
    "status": "open",
    "sharing": "none", 
    "due_date": "2025-12-31",
    "description": "Major release with new features"
  }
}
```

#### Version Fields
- **name** (required): Version name (e.g., "1.0.0", "Sprint 1")
- **status**: "open", "locked", or "closed"
- **sharing**: "none", "descendants", "hierarchy", "tree", or "system"
- **due_date**: Target date in YYYY-MM-DD format (optional)
- **description**: Version description (optional)
- **wiki_page_title**: Associated wiki page (optional)

#### Version Operations
- **List versions**: GET `/projects/{project_id}/versions.json`
- **Create version**: POST `/projects/{project_id}/versions.json`
- **Show version**: GET `/versions/{version_id}.json`
- **Update version**: PUT `/versions/{version_id}.json`
- **Delete version**: DELETE `/versions/{version_id}.json`

### Project Management (Full CRUD Support)
**✅ You CAN create, update, delete, and archive projects!**

#### Creating a Project
Use POST to `/projects.json`:
```json
{
  "project": {
    "name": "New Project",
    "identifier": "new-project",
    "description": "Project description",
    "is_public": true
  }
}
```

### Advanced Operations
- **Archive project**: PUT `/projects/{project_id}/archive.json`
- **Unarchive project**: PUT `/projects/{project_id}/unarchive.json`
- **Close project**: PUT `/projects/{project_id}/close.json`
- **Reopen project**: PUT `/projects/{project_id}/reopen.json`
- **Manage memberships**: POST/PUT/DELETE `/projects/{project_id}/memberships.json`
- **Upload files**: POST `/uploads.json` (use redmine_upload tool)
- **Download files**: GET `/attachments/download/{id}/{filename}` (use redmine_download tool)
