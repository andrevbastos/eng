import os
import sys
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório 'src' ao sys.path para importações funcionarem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database.base import Base
# Importar todos os modelos para garantir que o Base.metadata reconheça todas as tabelas
import models.demandas
import models.documentos
import models.pareceres
import models.subsidios
import models.tags

# Mock global do engine antes de qualquer serviço importá-lo
test_engine = create_engine("sqlite:///:memory:", echo=False)
import database.base
database.base.engine = test_engine

@pytest.fixture(scope="function")
def db_session():
    # Cria as tabelas no banco em memória global
    Base.metadata.create_all(test_engine)
    
    # Cria uma sessão
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    
    yield session
    
    # Após o teste: fecha a sessão e limpa as tabelas para o próximo teste
    session.close()
    Base.metadata.drop_all(test_engine)
