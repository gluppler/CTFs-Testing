# Forensics Quick Reference

```bash
# File analysis
file suspicious.file
strings suspicious.file | head -50
binwalk -e suspicious.file

# PCAP
tshark -r capture.pcap -Y 'http' 2>&1 | head -30
tcpdump -r capture.pcap -A | head -100

# Memory dump
volatility3 -f memory.dump windows.info
volatility3 -f memory.dump windows.pslist

# Stego
steghide extract -sf image.jpg
zsteg image.png
exiftool image.jpg

# PDF
pdfinfo doc.pdf
pdf-parser.py doc.pdf

# Disk image
mmls disk.img
fls -r disk.img
icat disk.img <inode>
```
