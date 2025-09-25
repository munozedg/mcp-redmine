# Sensai Projects Schema - Mejoras Recomendadas

## 🚨 ALTA PRIORIDAD

### 1. Cambiar Versión OpenAPI
```yaml
# CAMBIAR DE:
openapi: "3.1.0"
# A:
openapi: "3.0.3"
```

### 2. Añadir Tags para Organización
```yaml
tags:
  - name: Issues
    description: Issue management and tracking
  - name: Projects  
    description: Project management
  - name: Time Tracking
    description: Time entry management
  - name: Search
    description: Intelligent search and autocomplete
  - name: Attachments
    description: File management
```

### 3. Eliminar Endpoint Duplicado
- Remover la segunda instancia de `/search.json`
- Consolidar funcionalidad en una sola definición

### 4. Añadir Endpoints Críticos Faltantes

#### Time Entries (CRÍTICO para productividad)
```yaml
/time_entries.json:
  get:
    tags: [Time Tracking]
    summary: List time entries
    parameters:
      - name: project_id
      - name: issue_id  
      - name: user_id
      - name: from
      - name: to
  post:
    tags: [Time Tracking] 
    summary: Create time entry
```

#### Attachments (CRÍTICO para manejo de archivos)
```yaml
/attachments.json:
  get:
    tags: [Attachments]
    summary: List attachments
/attachments/{id}.json:
  get:
    tags: [Attachments]
    summary: Get attachment details
/uploads.json:
  post:
    tags: [Attachments]
    summary: Upload file
```

#### Issue Relations (IMPORTANTE para dependencias)
```yaml
/issues/{issue_id}/relations.json:
  get:
    tags: [Issues]
    summary: Get issue relations
  post:
    tags: [Issues]
    summary: Create issue relation
```

### 5. Completar Esquemas Críticos

#### Issue Schema Completo
```yaml
Issue:
  type: object
  properties:
    id: {type: integer}
    project: {$ref: '#/components/schemas/Project'}
    tracker: {$ref: '#/components/schemas/Tracker'}
    status: {$ref: '#/components/schemas/Status'}
    priority: {$ref: '#/components/schemas/Priority'}
    author: {$ref: '#/components/schemas/User'}
    assigned_to: {$ref: '#/components/schemas/User'}
    subject: {type: string}
    description: {type: string}
    start_date: {type: string, format: date}
    due_date: {type: string, format: date}
    done_ratio: {type: integer, minimum: 0, maximum: 100}
    estimated_hours: {type: number}
    spent_hours: {type: number}
    created_on: {type: string, format: date-time}
    updated_on: {type: string, format: date-time}
    closed_on: {type: string, format: date-time}
    parent: {$ref: '#/components/schemas/Issue'}
    children: 
      type: array
      items: {$ref: '#/components/schemas/Issue'}
    attachments:
      type: array  
      items: {$ref: '#/components/schemas/Attachment'}
    relations:
      type: array
      items: {$ref: '#/components/schemas/IssueRelation'}
    journals:
      type: array
      items: {$ref: '#/components/schemas/Journal'}
    custom_fields:
      type: array
      items: {$ref: '#/components/schemas/CustomField'}
    watchers:
      type: array
      items: {$ref: '#/components/schemas/User'}
```

#### TimeEntry Schema
```yaml
TimeEntry:
  type: object
  properties:
    id: {type: integer}
    project: {$ref: '#/components/schemas/Project'}
    issue: {$ref: '#/components/schemas/Issue'}
    user: {$ref: '#/components/schemas/User'}
    activity: {$ref: '#/components/schemas/TimeEntryActivity'}
    hours: {type: number}
    comments: {type: string}
    spent_on: {type: string, format: date}
    created_on: {type: string, format: date-time}
    updated_on: {type: string, format: date-time}
    custom_fields:
      type: array
      items: {$ref: '#/components/schemas/CustomField'}
```

#### Attachment Schema  
```yaml
Attachment:
  type: object
  properties:
    id: {type: integer}
    filename: {type: string}
    filesize: {type: integer}
    content_type: {type: string}
    description: {type: string}
    content_url: {type: string}
    thumbnail_url: {type: string}
    author: {$ref: '#/components/schemas/User'}
    created_on: {type: string, format: date-time}
```

## 🔄 MEDIA PRIORIDAD

### 6. Añadir Versiones y Custom Fields
```yaml
/projects/{project_id}/versions.json:
  get:
    tags: [Projects]
    summary: List project versions
  post:
    tags: [Projects]
    summary: Create version

/custom_fields.json:
  get:
    tags: [Configuration]
    summary: List available custom fields
```

### 7. Mejorar CustomField Schema
```yaml
CustomField:
  type: object
  properties:
    id: {type: integer}
    name: {type: string}
    value: {} # Puede ser string, number, array, boolean
    multiple: {type: boolean}
    field_format:
      type: string
      enum: [string, text, int, float, date, bool, user, version, 
             enumeration, key_value, link, attachment, list]
    possible_values:
      type: array
      items: {type: string}
    default_value: {}
    visible: {type: boolean}
    required: {type: boolean}
```

### 8. Añadir Parámetros Comunes
```yaml
components:
  parameters:
    offset:
      name: offset
      in: query
      schema: {type: integer, minimum: 0}
      description: Skip this number of results
    limit:
      name: limit  
      in: query
      schema: {type: integer, minimum: 1, maximum: 100}
      description: Max results per page
    include:
      name: include
      in: query
      schema: {type: string}
      description: Include additional data (comma-separated)
```

## ⚡ BAJA PRIORIDAD

### 9. Añadir Endpoints Adicionales
- `/groups.json` - Gestión de grupos
- `/roles.json` - Gestión de roles  
- `/projects/{id}/wiki/` - Wiki pages
- `/news.json` - Noticias del proyecto

### 10. Mejorar Documentación
- Añadir `externalDocs` a cada endpoint
- Añadir ejemplos en esquemas
- Mejorar descriptions

## 🎯 IMPLEMENTACIÓN SUGERIDA

### Fase 1 (Esta semana): 
- Cambiar versión OpenAPI
- Eliminar duplicados
- Añadir tags básicos
- Añadir time entries

### Fase 2 (Próxima semana):
- Completar esquemas Issue/Project  
- Añadir attachments y uploads
- Añadir relations

### Fase 3 (Futuro):
- Endpoints adicionales
- Mejorar documentación
- Optimizaciones de rendimiento

## ✅ MANTENER Funcionalidades Únicas Sensai

- ✅ Búsqueda inteligente con fuzzy matching
- ✅ Endpoint /autocomplete.json
- ✅ Campos personalizados IXA Colombia
- ✅ Queries predefinidos específicos
- ✅ Parámetros de búsqueda avanzados
- ✅ Context awareness para IXA Colombia