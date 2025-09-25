# Project Environment Information

This document contains key information about the specific Redmine environment structure to help with project management and API interactions for the IXA Colombia instance.

## Redmine Instance Details

- **Base URL**: https://proyectos.ixacolombia.com/
- **API Access**: Full read-write permissions available
- **Authentication**: API Key based authentication

## Project Structure

### Default Project: Operations
- **Project ID**: 1
- **Identifier**: "ops"
- **Status**: Active (Status ID: 1)
- **Visibility**: Public
- **Created**: March 15, 2025
- **Last Updated**: March 18, 2025

## Team Members & Roles

All members have Manager role (Role ID: 3):

1. **Alex Wilson** (ID: 5)
2. **Morgan Chen** (ID: 6) 
3. **Taylor Roberts** (ID: 7)
4. **Jordan Bailey** (ID: 8)

## Issue Categories

Available categories for the Operations project:

1. **Task - Technical** (ID: 1)
2. **Task - Advisory** (ID: 2)
3. **Deployment** (ID: 3)
4. **Task - Customer** (ID: 4)
5. **Task - Portal** (ID: 5)
6. **DEV** (ID: 6)

## Available Trackers

1. **Code** (ID: 1) - Default tracker
2. **Feature** (ID: 2)
3. **Support** (ID: 3)

## Issue Statuses

Status IDs identified in the system:

1. **New** (ID: 1, is_closed: true)
2. **In Progress** (ID: 2)
3. **Feedback** (ID: 4)
4. **Done** (ID: 5, is_closed: true)
5. **Cancelled** (ID: 6, is_closed: true)
6. **Backlog** (ID: 7, is_closed: true)
7. **Pipelined** (ID: 8)

## Custom Fields

1. **Pull Request Reviewers** (ID: 2, multiple: true)
2. **Pull Request Targeted Branches** (ID: 3, multiple: true)

## Workflow Guidelines

### Work Units (WU) Calculation
- Work Units are calculated at 8 hours (1 day) per unit
- Estimated hours should be set in hours (WU × 8)
- Always specify estimated_hours when creating issues

### Date Format Standards
- All dates must use "YYYY-MM-DD" format
- start_date and due_date are critical for project planning

### Default Assignments
- Default tracker is "Code" (ID: 1) for most issues
- All issues in the Operations project should have a category assigned
- Manager role (ID: 3) has full project access

## Common Project-Specific Endpoints

### Core Project APIs
- `/projects/ops.json` - Operations project details
- `/projects/ops/memberships.json` - Project members
- `/projects/ops/issue_categories.json` - Issue categories
- `/projects/ops/versions.json` - Project versions

### Issue Management
- `/issues.json?project_id=ops` - Issues for Operations project
- `/issues/{issue_id}.json` - Specific issue details
- `/trackers.json` - Available trackers

### Time Tracking
- `/time_entries.json?project_id=ops` - Time entries for Operations
- `/time_entry_activities.json` - Available activities

## Integration Notes

### Pull Request Integration
- Custom fields are available for PR reviewers and target branches
- Pull request workflow is integrated with issue tracking
- Use custom field IDs 2 and 3 for PR-related information

### Version Management Best Practices
- Create versions for major releases and sprints
- Use meaningful version names (e.g., "Sprint 1", "Release 2.1.0")
- Set due dates for proper project timeline management
- Use "open" status for active development versions

## Environment-Specific Tips

1. **For Operations Project Issues**:
   - Always assign to appropriate category (1-6)
   - Use "Code" tracker unless specifically a Feature or Support request
   - Assign to team members (IDs: 5, 6, 7, 8) based on expertise

2. **For Time Tracking**:
   - Log time against specific issues when possible
   - Use descriptive comments for time entries
   - Consider Work Unit calculations for estimation

3. **For Version Planning**:
   - Create versions before sprint/release planning
   - Link issues to versions using fixed_version_id
   - Update version status as development progresses

4. **For User Management**:
   - All current users have Manager role
   - New users can be assigned appropriate roles based on responsibilities
   - Check user availability before assignment

## Quick Reference Commands

### Get Project Information
```
GET /projects/ops.json?include=trackers,issue_categories,enabled_modules
```

### Create New Issue for Operations
```json
{
  "issue": {
    "project_id": "ops",
    "tracker_id": 1,
    "category_id": 1,
    "subject": "Issue title",
    "description": "Detailed description",
    "assigned_to_id": 5,
    "priority_id": 2
  }
}
```

### Create Version for Operations
```json
{
  "version": {
    "name": "Sprint 2025-Q4",
    "status": "open",
    "due_date": "2025-12-31",
    "description": "Q4 development sprint"
  }
}
```