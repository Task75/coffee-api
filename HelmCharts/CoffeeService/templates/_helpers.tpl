{{- define "coffee-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "coffee-api.fullname" -}}
{{- if .Values.nameOverride -}}
{{ .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- else if and .Release.Name (ne .Release.Name .Chart.Name) -}}
{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- else -}}
{{ .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}
{{- end }}

{{- define "coffee-api.labels" -}}
app.kubernetes.io/name: {{ include "coffee-api.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "coffee-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "coffee-api.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end }}

