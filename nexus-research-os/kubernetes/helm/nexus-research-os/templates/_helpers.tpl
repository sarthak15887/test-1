{{/*
Expand the name of the chart.
*/}}
{{- define "nexus-research-os.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "nexus-research-os.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create a fully qualified backend name.
*/}}
{{- define "nexus-research-os.backend.fullname" -}}
{{- printf "%s-backend" (include "nexus-research-os.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a fully qualified frontend name.
*/}}
{{- define "nexus-research-os.frontend.fullname" -}}
{{- printf "%s-frontend" (include "nexus-research-os.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nexus-research-os.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nexus-research-os.labels" -}}
helm.sh/chart: {{ include "nexus-research-os.chart" .context }}
{{ include "nexus-research-os.selectorLabels" (dict "component" .component "context" .context) }}
{{- if .context.Chart.AppVersion }}
app.kubernetes.io/version: {{ .context.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .context.Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nexus-research-os.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nexus-research-os.name" .context }}
app.kubernetes.io/instance: {{ .context.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "nexus-research-os.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "nexus-research-os.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
