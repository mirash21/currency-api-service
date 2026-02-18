# Currency Exchange Rate Service

Professional Python service for automated currency exchange rates collection from public APIs with PostgreSQL storage and advanced analytics.

## 🎯 Features

- **Automated Data Collection**: Scheduled API requests every 5 minutes
- **Reliable Storage**: PostgreSQL with foreign key relationships  
- **SQL Analytics**: Advanced JOIN queries for data analysis
- **Error Logging**: Comprehensive error handling with file rotation
- **Docker Ready**: Production containerized deployment
- **Modular Design**: Clean architecture with separated concerns

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/mirash21/currency-api-service.git
cd currency-api-service

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run service
python currency_service.py
```

### Docker Deployment

```bash
# Build and deploy
make first-run

# Monitor logs
make logs

# Run tests
make test
```

## 📊 Database Schema

Two related tables with foreign key constraint:

**Requests Table**
```sql
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT
);
```

**Responses Table** 
```sql
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES requests(id) ON DELETE CASCADE,
    currency_code VARCHAR(3) NOT NULL,
    rate NUMERIC(16, 8) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 SQL JOIN Queries

### Request History with Currency Rates
```sql
SELECT 
    r.id as request_id,
    r.timestamp as request_time,
    r.status,
    res.currency_code,
    res.rate
FROM requests r
LEFT JOIN responses res ON r.id = res.request_id
ORDER BY r.timestamp DESC;
```

### Aggregated Statistics
```sql  
SELECT 
    r.id,
    COUNT(res.id) as currency_count,
    STRING_AGG(res.currency_code || ': ' || res.rate::TEXT, ', ') as rates
FROM requests r
LEFT JOIN responses res ON r.id = res.request_id
GROUP BY r.id;
```

## 📁 Project Structure

```
├── config.py              # Configuration management
├── logger.py             # Logging system
├── database.py           # PostgreSQL operations  
├── api_client.py         # API client
├── currency_service.py   # Main service
├── demo_service.py       # Demo mode
├── test_service.py       # Testing suite
├── view_data.py          # Data inspection
├── run_sql_demo.py       # SQL demonstrations
├── sql_queries.sql       # SQL query library
├── requirements.txt      # Dependencies
├── .env.example         # Config template
├── Dockerfile           # Docker image
├── docker-compose.yml   # Orchestration
├── Makefile             # Commands
└── README.md            # Documentation
```

## 🧪 Testing

```bash
# Run all tests
python test_service.py

# Test database connection
python -c "from database import db_manager; print('Connected:', db_manager.connect())"

# Test API connectivity  
python -c "from api_client import api_client; print('API Status:', api_client.health_check())"
```

## 📈 Monitoring

- Console output with detailed operations
- Error logging to `error.log` with rotation
- Database records of all requests/responses
- Built-in statistics dashboard

## ⚙️ Configuration

Key `.env` parameters:
- `REQUEST_INTERVAL_MINUTES`: Collection frequency
- Database connection settings
- API key configuration
- Logging preferences

## 🛠 Technologies Used

- **Python 3.11** with modern libraries
- **PostgreSQL 15** for reliable storage
- **ExchangeRate-API** for currency data
- **Docker** for containerization
- **Schedule** for task scheduling
- **Psycopg2** for database connectivity

## 📄 License

MIT License - Open source and free to use.