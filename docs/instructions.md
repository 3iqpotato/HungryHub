# Инструкции за инсталация и стартиране на Django проекта

## 📋 Предварителни изисквания
- Python 3.8+ ([Download Python](https://www.python.org/downloads/))
- Git ([Download Git](https://git-scm.com/downloads))
- PyCharm Professional ([Download PyCharm](https://www.jetbrains.com/pycharm/download/))

## 🚀 Инсталация и настройка

1. **Клонирайте хранилището**:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   
2. **Създайте и активирайте виртуална среда**:
    ```bash
    # За Windows:
    python -m venv venv
    venv\Scripts\activate
    
    # За macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate
   
3. **Инсталирайте зависимостите**:
    ```bash
    pip install -r requirements.txt
   
4. **Приложете миграциите:**: 
    ```bash
    python manage.py migrate
   
5. **Стартирайте development сървъра**:
    ```bash
    Стартирайте development сървъра:
   
6. **Достъп до приложението**:

Отворете браузър на адрес: http://127.0.0.1:8000/