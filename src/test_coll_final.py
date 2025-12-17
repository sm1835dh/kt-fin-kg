#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수정된 init_db.py로 COLL_SET 테스트
"""

import os
import sys
sys.path.append('.')

from init_db import get_db_connection, load_data_to_table
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_coll_set_only():
    """COLL_SET만 테스트"""
    try:
        # COLL_SET 테이블만 생성하고 데이터 적재
        conn = get_db_connection()
        cursor = conn.cursor()

        # COLL_SET 테이블 재생성
        drop_create_sql = """
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
        """
        cursor.execute(drop_create_sql)
        conn.commit()
        cursor.close()
        conn.close()

        logger.info("COLL_SET 테이블 재생성 완료")

        # 데이터 적재 (첫 100개만)
        file_path = '../data/06_COLL_SET.dat'

        # 임시로 파일의 첫 100줄만 저장
        temp_file = '/tmp/coll_set_test.dat'
        with open(file_path, 'r', encoding='euc-kr') as infile:
            with open(temp_file, 'w', encoding='euc-kr') as outfile:
                for i, line in enumerate(infile):
                    if i >= 100:  # 100개만
                        break
                    outfile.write(line)

        # 데이터 적재
        file_lines, inserted, db_count = load_data_to_table('COLL_SET', temp_file)

        logger.info(f"결과: 파일라인={file_lines}, 삽입={inserted}, DB행수={db_count}")

        if file_lines == db_count:
            logger.info("✓ COLL_SET 테스트 성공!")
            return True
        else:
            logger.error("✗ COLL_SET 테스트 실패")
            return False

    except Exception as e:
        logger.error(f"오류: {e}")
        return False

if __name__ == "__main__":
    success = test_coll_set_only()
    if success:
        logger.info("COLL_SET 테이블이 정상적으로 처리됩니다. 전체 데이터 적재를 진행하세요.")
    else:
        logger.error("COLL_SET 테이블 처리에 문제가 있습니다.")