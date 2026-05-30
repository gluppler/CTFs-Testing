# Notebook-Converter-Pro

## Status: Solved

- URL: `http://154.57.164.67:31204`
- Stack: Flask + nbconvert (Jupyter notebook converter)

## Vulnerability Chain

### 1. LFI via Markdown Image Embedding
nbconvert's `HTMLExporter` has `embed_images=True`, which embeds local files referenced as Markdown images into the output as base64 data URIs.

**Payload in notebook cell:**
```
![db](/srv/app/data/app.db)
```
Upload as `.ipynb`, convert to HTML → the SQLite database is base64-embedded in the output.

### 2. Extract Admin Password
The SQLite `users` table stores passwords in plaintext:
```
admin | Vs78GuWxBT-fDKD-UiU | admin
```

### 3. Admin Panel — Enable Asset Storage
Login as admin → POST `/admin` with `asset_storage_enabled=on`. This enables markdown conversion attachment extraction.

### 4. Arbitrary File Write via Attachment Path Traversal
nbconvert's `ExtractAttachmentsPreprocessor` extracts notebook attachments. The attachment `name` field accepts `../` path traversal. When markdown conversion is in `saved_assets` mode, filenames are joined under the build directory without sanitization.

**Attack:**
- Create a notebook with an attachment named `../../../../app/converter/convert_job.py` containing a base64-encoded Python script
- Convert to markdown → attachment overwrites the live converter code

### 5. Trigger Flag Read
- The overwritten `convert_job.py` now runs `/readflag` on every conversion
- Submit a new HTML conversion job
- The output HTML contains the flag

## Flag
`HTB{y3t_4n0th3r_pyth0n_c0nv3rt3r_cve}`

## Key Takeaways
- nbconvert with `embed_images=True` is an LFI vector
- Plaintext passwords in SQLite
- Attachment extraction path traversal for arbitrary file write
- Chaining LFI → credential theft → admin access → file write → RCE
