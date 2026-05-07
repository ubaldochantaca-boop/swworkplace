\# Uso de Codex en este proyecto



\## Resumen de la corrección realizada



| Item | Detalle |

|------|---------|

| \*\*Fecha\*\* | 2026-05-07 |

| \*\*Error\*\* | `cannot find symbol: method acceptWaveform(byte\[],int)` en VoskService.java |

| \*\*Causa\*\* | La API de Vosk 0.3.45 usa `acceptWaveForm` (con F mayúscula), no `acceptWaveform` |

| \*\*Solución\*\* | Cambiar a `recognizer.acceptWaveForm(audioData, audioData.length)` |

| \*\*Herramienta\*\* | Codex (OpenAI) + revisión manual con `javap` |



\## Configuración de Codex utilizada



\- \*\*Archivo de instrucciones:\*\* `AGENTS.md` (creado en la raíz)

\- \*\*Rama de trabajo:\*\* `fix/vosk-acceptwaveform-error`

\- \*\*Comandos utilizados:\*\*

&#x20; - `@codex review` → Solicitar revisión

&#x20; - `@codex fix` → Aplicar corrección automática

&#x20; - Validación local con `mvn clean compile`



\## Estado actual del repositorio



\- \[x] Rama `fix/vosk-acceptwaveform-error` eliminada (local y remota)

\- \[x] Archivos temporales (`vosk-lib/`) eliminados

\- \[x] Pull Request mergeado y cerrado

\- \[x] Build exitoso: `mvn clean compile -DskipTests`

\- \[x] `git status` → `working tree clean`



\## Cómo usar Codex en el futuro



\### Prerrequisitos

1\. Tener `AGENTS.md` en la raíz con las instrucciones del proyecto

2\. GitHub repositorio con Codex habilitado



\### Flujo rápido

```bash

\# 1. Crear rama

git checkout -b fix/nombre-del-error



\# 2. Subir rama y crear PR

git push origin fix/nombre-del-error

\# (Crear PR en GitHub Web)



\# 3. En el PR comentar:

\# @codex review



\# 4. Si Codex sugiere corrección, comentar:

\# @codex fix



\# 5. Validar localmente

git pull origin fix/nombre-del-error

mvn clean compile  # o el comando de build correspondiente



\# 6. Mergear y limpiar

git checkout main

git pull origin main

git branch -d fix/nombre-del-error

git push origin --delete fix/nombre-del-error



Limitaciones detectadas de Codex

No conoce APIs específicas de versiones recientes



Puede sugerir métodos inexactos (ej. acceptWaveform vs acceptWaveForm)



Es necesario validar localmente cada corrección



Lección aprendida

Codex acelera la iteración, pero la validación humana y el conocimiento de herramientas como javap son irremplazables para encontrar la solución exacta.



Comandos útiles para inspeccionar APIs

bash

\# Descargar JAR de una librería

mvn dependency:copy -Dartifact=groupId:artifactId:version -DoutputDirectory=./temp-lib



\# Ver métodos de una clase

jar xf libreria.jar

javap -cp . paquete.Clase

\*Documentación generada el 2026-05-07 después de corrección exitosa con Codex\*





