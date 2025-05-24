## 🚀 Quickstart
Clone the repository:
```shell
git clone https://github.com/achmdrzl/Langgraph-Research-Assistant.git
cd Langgraph-Research-Assistant
```
Then edit the `.env` with your api key
```shell
cp .env.example .env
```

### Running with LangGraph

1. (Recommended) Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Init the database:


```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql
```
```sql
ALTER USER 'root'@'localhost'
  IDENTIFIED WITH mysql_native_password
  BY '123456789';
FLUSH PRIVILEGES;
exit
```
```bash
mysql -u root -p
Enter the password (123456789)

```sql
CREATE DATABASE llm_agent;
EXIT;
```
```bash
python3 init_db.py
```

3. Invoke the LLM

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
 Then connect to http://127.0.0.1:8000/ on your browser.
