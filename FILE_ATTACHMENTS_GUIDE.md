# File Attachments with Your Redmine GPT 📎

## Overview

Your GPT now supports **attaching files to issues** using the enhanced schema. This works through a 2-step process that mirrors how Redmine's API handles file uploads.

## How File Attachments Work

### Step 1: Upload File
First, the file needs to be uploaded to get an upload token:

```json
POST /uploads.json
Content-Type: application/octet-stream
(binary file content)
```

**Response:**
```json
{
  "upload": {
    "id": 123,
    "token": "abc123def456",
    "filename": "document.pdf", 
    "filesize": 524288,
    "content_type": "application/pdf"
  }
}
```

### Step 2: Attach to Issue
Use the token when creating or updating an issue:

```json
{
  "issue": {
    "project_id": 1,
    "subject": "Issue with attachment",
    "description": "Please see attached document",
    "uploads": [
      {
        "token": "abc123def456",
        "filename": "document.pdf",
        "description": "Supporting documentation"
      }
    ]
  }
}
```

## GPT Usage Examples

### Creating an Issue with File Attachment

**User:** "Create an issue in project 5 with subject 'Bug Report' and attach this error log file"

**Your GPT will:**
1. **Upload the file** using `POST /uploads.json` 
2. **Get the upload token** from the response
3. **Create the issue** using `POST /issues.json` with the token in the `uploads` array

### Adding Files to Existing Issues

**User:** "Add this screenshot to issue #123"

**Your GPT will:**
1. **Upload the file** using `POST /uploads.json`
2. **Update the issue** using `PUT /issues/{id}.json` with the token in the `uploads` array

## Schema Features Added

### 🆕 New Endpoint: `/uploads.json`
- **Operation**: `uploadFile`
- **Method**: `POST` 
- **Purpose**: Upload files and get tokens
- **Content-Type**: `application/octet-stream` (for binary files)

### 🔧 Enhanced Endpoints: 
- **`createIssue`** (POST /issues.json) - now supports `uploads` array
- **`updateIssue`** (PUT /issues/{id}.json) - now supports `uploads` array

### 📋 Upload Object Schema:
```json
{
  "token": "string", // Required: token from upload endpoint
  "filename": "string", // Required: original filename  
  "description": "string" // Optional: attachment description
}
```

## Testing File Attachments

You can test this functionality by:

1. **Uploading your updated schema** to your OpenAI custom GPT
2. **Ask your GPT to create an issue with a file attachment**
3. **Verify the file appears** in the Redmine issue

### Example Commands:
- "Create a bug report and attach this screenshot"  
- "Add this document to issue #456"
- "Upload this log file to the server maintenance issue"

## Technical Notes

### File Types Supported
- Any file type Redmine accepts (PDFs, images, documents, logs, etc.)
- File size limits depend on your Redmine server configuration

### Authentication
- Uses the same query parameter authentication: `?key=YOUR_API_KEY`
- File uploads require the same API permissions as issue creation/editing

### GPT Limitations
- OpenAI GPTs can handle file uploads from users
- The GPT will automatically handle the 2-step process (upload → attach)
- Binary file content is handled transparently by the GPT

## Success! 🎉

Your Redmine GPT can now:
- ✅ **Accept files from users** during conversations  
- ✅ **Upload files to Redmine** automatically
- ✅ **Attach them to new issues** seamlessly
- ✅ **Add files to existing issues** with simple commands

This makes your GPT much more powerful for project management workflows!