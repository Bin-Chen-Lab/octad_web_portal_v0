INSERT INTO job_details (job_id) select id from job;
ALTER TABLE `octad`.`job_details`
CHANGE COLUMN `case_age_in_year` `case_age_in_year` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `ctrl_age_in_year` `ctrl_age_in_year` VARCHAR(50) NULL DEFAULT NULL ;


ALTER TABLE `octad`.`job_details`
CHANGE COLUMN `case_EGFR` `case_EGFR` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `case_IDH1` `case_IDH1` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `case_IDH2` `case_IDH2` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `case_TP53` `case_TP53` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `ctrl_EGFR` `ctrl_EGFR` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `ctrl_IDH1` `ctrl_IDH1` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `ctrl_IDH2` `ctrl_IDH2` VARCHAR(50) NULL DEFAULT NULL ,
CHANGE COLUMN `ctrl_TP53` `ctrl_TP53` VARCHAR(50) NULL DEFAULT NULL ;



--If IP is not accessible in network execute following command, iptables -I INPUT -p tcp --dport 5000 -j ACCEPT