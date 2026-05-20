# Install Dependency Python

Buka terminal:

```bash
cd ai-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

---

# Menjalankan Program

## Jalankan AI Service

Buka terminal pertama:

```bash
cd ai-service
venv\Scripts\activate
python app.py
```

## Jalankan Spring Boot

Buka terminal kedua:

```bash
mvnw.cmd spring-boot:run
```

---

# Buka Aplikasi

Buka browser:

```text
http://localhost:8080
```
