CREATE SEQUENCE seq_system_disk_audit_sno
START WITH 1
INCREMENT BY 1
MAXVALUE 999999
NOCYCLE
NOCACHE;

CREATE TABLE system_disk_audit
(
    sno NUMBER PRIMARY KEY DEFAULT seq_system_disk_audit_sno.NEXTVAL,
    deviceid VARCHAR2(20),
    freespace_mb NUMBER,
    size_mb NUMBER,
    created_date DATE DEFAULT SYSDATE
);

CREATE SEQUENCE seq_app_logger_id
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

CREATE TABLE app_logger
(
    log_id        NUMBER PRIMARY KEY,
    log_level     VARCHAR2(20),
    module_name   VARCHAR2(100),
    log_message   VARCHAR2(4000),
    created_date  DATE DEFAULT SYSDATE
);