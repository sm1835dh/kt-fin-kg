#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COLL_SET 테이블 테스트 스크립트
"""

import os
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': os.getenv('PGHOST'),
    'port': os.getenv('PGPORT', '5432'),
    'database': os.getenv('PGDATABASE'),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD')
}

def get_db_connection():
    """PostgreSQL 데이터베이스 연결을 반환합니다."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        raise

def test_coll_set():
    """COLL_SET 테이블 10개 데이터 테스트"""

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS COLL_SET")

        # 새 테이블 생성 (8개 컬럼으로)
        create_table_sql = """
            CREATE TABLE COLL_SET (
                담보여신계좌번호 CHAR(20) PRIMARY KEY,
                대출잔액 DECIMAL(18,2),
                담보평가금액 DECIMAL(18,2),
                담보대대출비율 DECIMAL(10,6),
                소재지번호 CHAR(9),
                법정동코드 CHAR(10),
                주담보구분 CHAR(3),
                추가컬럼 TEXT
            );
        """
        cursor.execute(create_table_sql)
        logger.info("COLL_SET 테이블 생성 완료")

        # 10개 데이터 읽기 및 테스트
        file_path = '../data/06_COLL_SET.dat'
        batch_data = []

        # EUC-KR 인코딩으로 파일 읽기
        with open(file_path, 'r', encoding='euc-kr') as f:
            for i, line in enumerate(f):
                if i >= 10:  # 10개만 테스트
                    break

                line = line.strip()
                if not line:
                    continue

                # ^ 구분자로 분할
                columns = line.split('^')
                logger.info(f"라인 {i+1}: {len(columns)}개 컬럼")

                # 8개 컬럼으로 조정
                if len(columns) < 8:
                    columns.extend([None] * (8 - len(columns)))
                elif len(columns) > 8:
                    columns = columns[:8]

                # 빈 문자열을 NULL로 변환 및 데이터 정리
                processed_columns = []
                for j, col in enumerate(columns):
                    if col and col.strip():
                        col = col.strip()
                        # 숫자 필드 처리 (소수점 자리수 제한)
                        if j in [1, 2]:  # 대출잔액, 담보평가금액
                            try:
                                col = str(round(float(col), 2))
                            except:
                                pass
                        elif j == 3:  # 담보대대출비율
                            try:
                                col = str(round(float(col), 6))
                            except:
                                pass
                        processed_columns.append(col)
                    else:
                        processed_columns.append(None)

                batch_data.append(processed_columns)
                logger.info(f"처리된 데이터: {processed_columns}")

        # 배치 삽입
        insert_query = "INSERT INTO COLL_SET VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

        execute_batch(cursor, insert_query, batch_data, page_size=10)
        conn.commit()

        logger.info(f"성공적으로 {len(batch_data)}개 행 삽입 완료")

        # 결과 확인
        cursor.execute("SELECT COUNT(*) FROM COLL_SET")
        count = cursor.fetchone()[0]
        logger.info(f"테이블 행 수: {count}")

        # 샘플 데이터 조회
        cursor.execute("SELECT * FROM COLL_SET LIMIT 3")
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"샘플 데이터: {row}")

    except Exception as e:
        logger.error(f"오류: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_coll_set()