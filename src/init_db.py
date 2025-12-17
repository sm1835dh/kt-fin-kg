#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 데이터베이스 초기화 및 데이터 적재 스크립트
"""

import os
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import logging
from pathlib import Path

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

def create_tables():
    """모든 테이블을 생성합니다."""

    # DDL 쿼리들
    table_ddls = {
        'CORP_PROF': """
            CREATE TABLE IF NOT EXISTS CORP_PROF (
                기업식별자 CHAR(10) PRIMARY KEY,
                크레탑업체명 VARCHAR(170),
                크레탑업종구분 CHAR(6),
                사업자번호 CHAR(10),
                소재지우편번호 CHAR(6),
                법인등록번호 CHAR(13)
            );
        """,

        'CUST_MST': """
            CREATE TABLE IF NOT EXISTS CUST_MST (
                고객식별자 CHAR(10) PRIMARY KEY,
                고객고유번호 CHAR(20),
                고객고유번호구분 CHAR(2),
                고객유형분류구분 CHAR(1)
            );
        """,

        'CORP_BIZ_MAP': """
            CREATE TABLE IF NOT EXISTS CORP_BIZ_MAP (
                고객식별자 CHAR(10) PRIMARY KEY,
                법인고객식별자 CHAR(10)
            );
        """,

        'LOAN_CTRT': """
            CREATE TABLE IF NOT EXISTS LOAN_CTRT (
                계좌번호 CHAR(20),
                상품계약회차 DECIMAL(7),
                계약자고객식별자 CHAR(10),
                상품계약회차상태구분 CHAR(1),
                상품코드 CHAR(12),
                상품계약회차약정년월일 CHAR(8),
                상품계약회차만기년월일 CHAR(8),
                관리부점코드 CHAR(4),
                통화코드 CHAR(3),
                대줄잔액 DECIMAL(18,0),
                상환방법구분 CHAR(2),
                한도계좌관리구분 CHAR(1),
                자동대출수신계좌번호 CHAR(20),
                PRIMARY KEY (계좌번호, 상품계약회차)
            );
        """,

        'PRD_MST': """
            CREATE TABLE IF NOT EXISTS PRD_MST (
                상품정보유형구분 CHAR(2),
                상품코드 CHAR(12),
                상품한글명 VARCHAR(150),
                상품상태구분 CHAR(2),
                판매시작년월일 CHAR(8),
                판매종료년월일 CHAR(8),
                PRIMARY KEY (상품정보유형구분, 상품코드)
            );
        """,

        'COLL_SET': """
            DROP TABLE IF EXISTS COLL_SET;
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
        """,

        'CAI_TXN': """
            CREATE TABLE IF NOT EXISTS CAI_TXN (
                판매사업자번호 CHAR(10),
                구매사업자번호 CHAR(10),
                매출거래금액 DECIMAL(18,0)
            );
        """,

        'KSIC_CD': """
            CREATE TABLE IF NOT EXISTS KSIC_CD (
                세세분류코드 CHAR(5) PRIMARY KEY,
                세세분류명 VARCHAR(300),
                세분류코드 CHAR(4),
                세분류명 VARCHAR(300),
                소분류코드 CHAR(3),
                소분류명 VARCHAR(300),
                중분류코드 CHAR(2),
                중분류명 VARCHAR(300),
                대분류코드 CHAR(1),
                대분류명 VARCHAR(300)
            );
        """,

        'ADM_DONG_CD': """
            CREATE TABLE IF NOT EXISTS ADM_DONG_CD (
                광역시도코드 CHAR(2),
                시군구코드 CHAR(2),
                구코드 CHAR(1),
                읍면동코드 CHAR(3),
                리코드 CHAR(2),
                기준년 CHAR(4),
                법정동코드 CHAR(10),
                광역시도명 VARCHAR(30),
                시군구명 VARCHAR(30),
                읍면동명 VARCHAR(30),
                리명 VARCHAR(30),
                PRIMARY KEY (광역시도코드, 시군구코드, 구코드, 읍면동코드, 리코드, 기준년)
            );
        """,

        'ZIP_CD': """
            CREATE TABLE IF NOT EXISTS ZIP_CD (
                우편번호 CHAR(6) PRIMARY KEY,
                한글시도명 VARCHAR(40),
                한글시군구명 VARCHAR(40),
                한글읍면동명 VARCHAR(40)
            );
        """,

        'BRANCH_CD': """
            CREATE TABLE IF NOT EXISTS BRANCH_CD (
                부점코드 CHAR(4) PRIMARY KEY,
                부점한글명 VARCHAR(20),
                우편번호 CHAR(6),
                부점구분 CHAR(2),
                출장소모점부점코드 CHAR(4)
            );
        """,

        'CMN_CD': """
            CREATE TABLE IF NOT EXISTS CMN_CD (
                코드식별자 CHAR(9),
                코드 CHAR(14),
                유효시작년월일 CHAR(8),
                유효종료년월일 CHAR(8),
                코드내용 VARCHAR(1000),
                PRIMARY KEY (코드식별자, 코드, 유효시작년월일)
            );
        """
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for table_name, ddl in table_ddls.items():
            logger.info(f"{table_name} 테이블 생성 중...")
            cursor.execute(ddl)
            logger.info(f"{table_name} 테이블 생성 완료")

        conn.commit()
        logger.info("모든 테이블 생성 완료")

    except Exception as e:
        logger.error(f"테이블 생성 오류: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def load_data_to_table(table_name, file_path, batch_size=10000):
    """특정 테이블에 데이터를 bulk로 적재합니다."""

    # 테이블별 컬럼 수 정의
    column_counts = {
        'CORP_PROF': 6,
        'CUST_MST': 4,
        'CORP_BIZ_MAP': 2,
        'LOAN_CTRT': 13,
        'PRD_MST': 6,
        'COLL_SET': 8,
        'CAI_TXN': 3,
        'KSIC_CD': 10,
        'ADM_DONG_CD': 11,
        'ZIP_CD': 4,
        'BRANCH_CD': 5,
        'CMN_CD': 5
    }

    if table_name not in column_counts:
        raise ValueError(f"지원하지 않는 테이블: {table_name}")

    expected_columns = column_counts[table_name]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 기존 데이터 삭제
        cursor.execute(f"DELETE FROM {table_name}")

        # 파일 읽기 및 데이터 배치 처리
        file_line_count = 0
        inserted_count = 0
        batch_data = []

        placeholders = ','.join(['%s'] * expected_columns)
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"

        # 한글 데이터 처리를 위한 인코딩 시도
        encodings_to_try = ['euc-kr', 'cp949', 'utf-8']
        file_handle = None

        for encoding in encodings_to_try:
            try:
                file_handle = open(file_path, 'r', encoding=encoding)
                # 첫 줄을 읽어서 인코딩이 올바른지 확인
                pos = file_handle.tell()
                test_line = file_handle.readline()
                file_handle.seek(pos)
                logger.info(f"{table_name}: {encoding} 인코딩 사용")
                break
            except (UnicodeDecodeError, Exception):
                if file_handle:
                    file_handle.close()
                continue

        if not file_handle:
            raise ValueError(f"지원하는 인코딩을 찾을 수 없습니다: {file_path}")

        with file_handle:
            for line in file_handle:
                file_line_count += 1
                line = line.strip()
                if not line:
                    continue

                # ^ 구분자로 분할
                columns = line.split('^')

                # 컬럼 수 확인 및 조정
                if len(columns) < expected_columns:
                    # 부족한 컬럼은 NULL로 패딩
                    columns.extend([None] * (expected_columns - len(columns)))
                elif len(columns) > expected_columns:
                    # 초과하는 컬럼은 제거
                    columns = columns[:expected_columns]

                # 빈 문자열을 NULL로 변환 및 데이터 정리
                processed_columns = []
                for j, col in enumerate(columns):
                    if col and col.strip():
                        col = col.strip()
                        # COLL_SET 테이블의 숫자 필드 처리
                        if table_name == 'COLL_SET':
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

                # 배치 크기에 도달하면 일괄 삽입
                if len(batch_data) >= batch_size:
                    try:
                        execute_batch(cursor, insert_query, batch_data, page_size=batch_size)
                        inserted_count += len(batch_data)
                        logger.info(f"{table_name}: {inserted_count}개 행 삽입 완료")
                        batch_data = []
                    except Exception as e:
                        logger.error(f"배치 삽입 실패: {e}")
                        conn.rollback()
                        raise

        # 남은 데이터 삽입
        if batch_data:
            try:
                execute_batch(cursor, insert_query, batch_data, page_size=len(batch_data))
                inserted_count += len(batch_data)
                logger.info(f"{table_name}: 마지막 {len(batch_data)}개 행 삽입 완료")
            except Exception as e:
                logger.error(f"마지막 배치 삽입 실패: {e}")
                conn.rollback()
                raise

        conn.commit()
        logger.info(f"{table_name}: 파일 라인 수 {file_line_count}, 삽입된 행 수 {inserted_count}")

        # 테이블 행 수 확인
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        db_count = cursor.fetchone()[0]

        logger.info(f"{table_name}: 데이터베이스 행 수 {db_count}")

        return file_line_count, inserted_count, db_count

    except Exception as e:
        logger.error(f"{table_name} 데이터 적재 오류: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def count_file_lines(file_path):
    """파일의 라인 수를 계산합니다."""
    encodings_to_try = ['euc-kr', 'cp949', 'utf-8']

    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return sum(1 for line in f if line.strip())
        except (UnicodeDecodeError, Exception):
            continue

    raise ValueError(f"지원하는 인코딩을 찾을 수 없습니다: {file_path}")

def main():
    """메인 실행 함수"""
    try:
        logger.info("데이터베이스 초기화 시작")

        # 1. 테이블 생성
        logger.info("=== 테이블 생성 시작 ===")
        create_tables()

        # 2. 데이터 적재
        logger.info("=== 데이터 적재 시작 ===")

        data_dir = Path("../data")

        # 파일과 테이블 매핑
        file_table_mapping = {
            "01_CORP_PROF.dat": "CORP_PROF",
            "02_CUST_MST.dat": "CUST_MST",
            "03_CORP_BIZ_MAP.dat": "CORP_BIZ_MAP",
            "04_LOAN_CTRT.dat": "LOAN_CTRT",
            "05_PRD_MST.dat": "PRD_MST",
            "06_COLL_SET.dat": "COLL_SET",
            "07_CAI_TXN.dat": "CAI_TXN",
            "08_KSIC_CD.dat": "KSIC_CD",
            "09_ADM_DONG_CD.dat": "ADM_DONG_CD",
            "10_ZIP_CD.dat": "ZIP_CD",
            "11_BRANCH_CD.dat": "BRANCH_CD",
            "12_CMN_CD.dat": "CMN_CD"
        }

        results = {}

        for file_name, table_name in file_table_mapping.items():
            file_path = data_dir / file_name
            if file_path.exists():
                logger.info(f"{table_name} 데이터 적재 시작...")
                file_lines, inserted, db_count = load_data_to_table(table_name, str(file_path))
                results[table_name] = {
                    'file_lines': file_lines,
                    'inserted': inserted,
                    'db_count': db_count,
                    'match': file_lines == db_count
                }
            else:
                logger.warning(f"파일을 찾을 수 없습니다: {file_path}")

        # 3. 결과 요약
        logger.info("=== 적재 결과 요약 ===")
        all_match = True

        for table_name, result in results.items():
            status = "✓" if result['match'] else "✗"
            logger.info(f"{table_name}: 파일라인={result['file_lines']}, DB행수={result['db_count']} {status}")
            if not result['match']:
                all_match = False

        if all_match:
            logger.info("모든 테이블의 데이터 적재가 성공적으로 완료되었습니다!")
        else:
            logger.warning("일부 테이블에서 파일 라인 수와 DB 행 수가 일치하지 않습니다.")

    except Exception as e:
        logger.error(f"작업 실행 중 오류: {e}")
        raise

if __name__ == "__main__":
    main()