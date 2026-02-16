
# Deep Dataset Exploration Report

**Generated:** 2026-02-06 03:00:39

**Dataset:** AIT LDSv2.0 -- russellmitchell testbed

**Dataset Root:** `local path to dataset`


## 1. File Inventory

Scanning all hosts in `gather/` for log files...


| Host                | File                                                                                                           |        Size (KB) | Lines      |
|:--------------------|:---------------------------------------------------------------------------------------------------------------|-----------------:|:-----------|
| attacker_0          | attacker_0/logs/ait.aecid.attacker.wpdiscuz/sm.log                                                             |   1900.1         | 509        |
| attacker_0          | attacker_0/logs/ait.aecid.attacker.wpdiscuz/traffic.json                                                       | 532667           | 650,398    |
| attacker_0          | attacker_0/logs/ait.aecid.attacker.wpdiscuz/traffic.pcap                                                       | 316545           | 17,546,982 |
| attacker_0          | attacker_0/logs/attacks.log                                                                                    |      2.5         | 56         |
| attacker_0          | attacker_0/logs/dnsteal/2010_invoices.xlsx                                                                     |     13.6         | 96         |
| attacker_0          | attacker_0/logs/dnsteal/2011_invoices.xlsx                                                                     |     16           | 131        |
| attacker_0          | attacker_0/logs/dnsteal/2012_invoices.xlsx                                                                     |     10           | 61         |
| attacker_0          | attacker_0/logs/dnsteal/2013_invoices.xlsx                                                                     |     17.8         | 155        |
| attacker_0          | attacker_0/logs/dnsteal/2014_invoices.xlsx                                                                     |     18.5         | 147        |
| attacker_0          | attacker_0/logs/dnsteal/2015_invoices.xlsx                                                                     |     19.3         | 172        |
| attacker_0          | attacker_0/logs/dnsteal/2016_invoices.xlsx                                                                     |     15.9         | 117        |
| attacker_0          | attacker_0/logs/dnsteal/2017_invoices.xlsx                                                                     |      9.7         | 79         |
| attacker_0          | attacker_0/logs/dnsteal/2018_invoices.xlsx                                                                     |     15.4         | 107        |
| attacker_0          | attacker_0/logs/dnsteal/2019_invoices.xlsx                                                                     |     21.3         | 158        |
| attacker_0          | attacker_0/logs/dnsteal/2020_invoices.xlsx                                                                     |     18.8         | 129        |
| attacker_0          | attacker_0/logs/dnsteal/HuangInc.docx                                                                          |     23.7         | 186        |
| attacker_0          | attacker_0/logs/dnsteal/VasquezWangAndFox.docx                                                                 |     23.8         | 183        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2013.xlsx                                                                    |    100.6         | 651        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2014.xlsx                                                                    |     84.9         | 586        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2015.xlsx                                                                    |    105.8         | 650        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2016.xlsx                                                                    |    100.9         | 715        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2017.xlsx                                                                    |    104.2         | 695        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2018.xlsx                                                                    |     93.5         | 597        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2019.xlsx                                                                    |    103.8         | 703        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2020.xlsx                                                                    |    105           | 693        |
| attacker_0          | attacker_0/logs/dnsteal/customers_2021.xlsx                                                                    |    105.9         | 689        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2013.xlsx                                                                      |     96.4         | 756        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2014.xlsx                                                                      |     95.5         | 774        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2015.xlsx                                                                      |     96.8         | 722        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2016.xlsx                                                                      |     96.4         | 676        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2017.xlsx                                                                      |     96.3         | 817        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2018.xlsx                                                                      |     94.4         | 762        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2019.xlsx                                                                      |     95.7         | 741        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2020.xlsx                                                                      |     97.3         | 746        |
| attacker_0          | attacker_0/logs/dnsteal/payroll_2021.xlsx                                                                      |     97.6         | 786        |
| attacker_0          | attacker_0/logs/dnsteal/traffic.json                                                                           |  63918.6         | 41,436     |
| attacker_0          | attacker_0/logs/dnsteal/traffic.pcap                                                                           | 431705           | 18,365,759 |
| attacker_0          | attacker_0/logs/dnsteal.log                                                                                    |   2542           | 20,054     |
| cloud_share         | cloud_share/logs/apache2/access.log                                                                            |      0           | 0          |
| cloud_share         | cloud_share/logs/apache2/error.log.1                                                                           |      0.3         | 2          |
| cloud_share         | cloud_share/logs/apache2/error.log.2                                                                           |     16.4         | 241        |
| cloud_share         | cloud_share/logs/apache2/error.log.3                                                                           |     45.7         | 675        |
| cloud_share         | cloud_share/logs/apache2/error.log.4                                                                           |      0.1         | 1          |
| cloud_share         | cloud_share/logs/apache2/other_vhosts_access.log                                                               |      0           | 0          |
| cloud_share         | cloud_share/logs/apache2/other_vhosts_access.log.1                                                             |   1479.1         | 5,546      |
| cloud_share         | cloud_share/logs/apache2/other_vhosts_access.log.2                                                             |   1904.4         | 6,954      |
| cloud_share         | cloud_share/logs/apache2/other_vhosts_access.log.3                                                             |   2112.5         | 7,591      |
| cloud_share         | cloud_share/logs/apache2/other_vhosts_access.log.4                                                             |   2045.4         | 7,409      |
| cloud_share         | cloud_share/logs/audit/audit.log                                                                               |    807.9         | 4,588      |
| cloud_share         | cloud_share/logs/auth.log                                                                                      |     58.5         | 592        |
| cloud_share         | cloud_share/logs/auth.log.1                                                                                    |     77.7         | 784        |
| cloud_share         | cloud_share/logs/redis/redis-server.log                                                                        |      0           | 0          |
| cloud_share         | cloud_share/logs/redis/redis-server.log.1                                                                      |      2.7         | 33         |
| cloud_share         | cloud_share/logs/redis/redis.log                                                                               |     37.5         | 580        |
| cloud_share         | cloud_share/logs/suricata/eve.json                                                                             | 295014           | 86,092     |
| cloud_share         | cloud_share/logs/suricata/fast.log                                                                             |     12.7         | 56         |
| cloud_share         | cloud_share/logs/suricata/log.pcap.1642684647                                                                  | 513537           | 4,657,618  |
| cloud_share         | cloud_share/logs/suricata/stats.log                                                                            | 234036           | 2,974,744  |
| cloud_share         | cloud_share/logs/suricata/suricata-start.log                                                                   |      1.1         | 12         |
| cloud_share         | cloud_share/logs/suricata/suricata.log                                                                         |    245.6         | 1,100      |
| cloud_share         | cloud_share/logs/syslog.1                                                                                      |     26.7         | 284        |
| cloud_share         | cloud_share/logs/syslog.2                                                                                      |     36.7         | 395        |
| cloud_share         | cloud_share/logs/syslog.3                                                                                      |     36.8         | 391        |
| cloud_share         | cloud_share/logs/syslog.4                                                                                      |     58           | 622        |
| davey_mail          | davey_mail/logs/auth.log                                                                                       |     31           | 321        |
| davey_mail          | davey_mail/logs/auth.log.1                                                                                     |    123.6         | 1,027      |
| davey_mail          | davey_mail/logs/exim4/mainlog                                                                                  |      0.1         | 2          |
| davey_mail          | davey_mail/logs/exim4/mainlog.1                                                                                |     98.8         | 602        |
| davey_mail          | davey_mail/logs/exim4/mainlog.2                                                                                |    100.2         | 618        |
| davey_mail          | davey_mail/logs/exim4/mainlog.3                                                                                |    107.8         | 636        |
| davey_mail          | davey_mail/logs/exim4/mainlog.4                                                                                |    146.3         | 909        |
| davey_mail          | davey_mail/logs/horde/horde-access.log                                                                         |   1033.7         | 3,742      |
| davey_mail          | davey_mail/logs/horde/horde-error.log                                                                          |      0           | 0          |
| davey_mail          | davey_mail/logs/mail.info                                                                                      |    189.1         | 1,513      |
| davey_mail          | davey_mail/logs/mail.info.1                                                                                    |    245.8         | 1,967      |
| davey_mail          | davey_mail/logs/mail.log                                                                                       |    189.1         | 1,513      |
| davey_mail          | davey_mail/logs/mail.log.1                                                                                     |    245.8         | 1,967      |
| davey_mail          | davey_mail/logs/mail.warn                                                                                      |      0           | 0          |
| davey_mail          | davey_mail/logs/mail.warn.1                                                                                    |      0.4         | 4          |
| davey_mail          | davey_mail/logs/messages                                                                                       |     58.7         | 319        |
| davey_mail          | davey_mail/logs/messages.1                                                                                     |    119.9         | 802        |
| davey_mail          | davey_mail/logs/syslog                                                                                         |     25.6         | 316        |
| davey_mail          | davey_mail/logs/syslog.1                                                                                       |    163.1         | 1,263      |
| davey_mail          | davey_mail/logs/syslog.2                                                                                       |    176.2         | 1,357      |
| davey_mail          | davey_mail/logs/syslog.3                                                                                       |    183.7         | 1,408      |
| davey_mail          | davey_mail/logs/syslog.4                                                                                       |    400.8         | 3,449      |
| davey_mail          | davey_mail/logs/user.log                                                                                       |     58.5         | 318        |
| davey_mail          | davey_mail/logs/user.log.1                                                                                     |     93.5         | 494        |
| ext_user_0          | ext_user_0/logs/sm.log                                                                                         |   2422.4         | 6,140      |
| ext_user_1          | ext_user_1/logs/sm.log                                                                                         |   1805.5         | 4,376      |
| ext_user_2          | ext_user_2/logs/sm.log                                                                                         |   2073.1         | 5,045      |
| inet-dns            | inet-dns/logs/auth.log                                                                                         |     12.4         | 129        |
| inet-dns            | inet-dns/logs/auth.log.1                                                                                       |     38.1         | 355        |
| inet-dns            | inet-dns/logs/dnsmasq.log                                                                                      |  31499           | 264,982    |
| inet-dns            | inet-dns/logs/syslog                                                                                           |     12.6         | 155        |
| inet-dns            | inet-dns/logs/syslog.1                                                                                         |      4.9         | 53         |
| inet-dns            | inet-dns/logs/syslog.2                                                                                         |      5.1         | 55         |
| inet-dns            | inet-dns/logs/syslog.3                                                                                         |      4.4         | 45         |
| inet-dns            | inet-dns/logs/syslog.4                                                                                         |    125.4         | 1,356      |
| inet-firewall       | inet-firewall/logs/audit/audit.log                                                                             |    126.3         | 726        |
| inet-firewall       | inet-firewall/logs/auth.log                                                                                    |      9.1         | 92         |
| inet-firewall       | inet-firewall/logs/auth.log.1                                                                                  |     12.2         | 124        |
| inet-firewall       | inet-firewall/logs/dnsmasq.log                                                                                 |  31473.2         | 275,900    |
| inet-firewall       | inet-firewall/logs/kern.log                                                                                    |     59.6         | 441        |
| inet-firewall       | inet-firewall/logs/kern.log.1                                                                                  |    112.4         | 991        |
| inet-firewall       | inet-firewall/logs/shorewall-init.log                                                                          |      0           | 0          |
| inet-firewall       | inet-firewall/logs/shorewall-init.log.1                                                                        |     18.1         | 310        |
| inet-firewall       | inet-firewall/logs/suricata/eve.json                                                                           | 396315           | 272,428    |
| inet-firewall       | inet-firewall/logs/suricata/fast.log                                                                           |   1130.4         | 5,724      |
| inet-firewall       | inet-firewall/logs/suricata/log.pcap.1642684610                                                                |      1.0123e+06  | 8,881,333  |
| inet-firewall       | inet-firewall/logs/suricata/log.pcap.1642771729                                                                |      1.00973e+06 | 8,677,353  |
| inet-firewall       | inet-firewall/logs/suricata/log.pcap.1642957916                                                                | 770704           | 8,148,245  |
| inet-firewall       | inet-firewall/logs/suricata/stats.log                                                                          | 258576           | 3,267,903  |
| inet-firewall       | inet-firewall/logs/suricata/suricata-start.log                                                                 |      1.1         | 12         |
| inet-firewall       | inet-firewall/logs/suricata/suricata.log                                                                       |    245.8         | 1,102      |
| inet-firewall       | inet-firewall/logs/syslog.1                                                                                    |     27.6         | 225        |
| inet-firewall       | inet-firewall/logs/syslog.2                                                                                    |     40.7         | 308        |
| inet-firewall       | inet-firewall/logs/syslog.3                                                                                    |     38.3         | 316        |
| inet-firewall       | inet-firewall/logs/syslog.4                                                                                    |     41.6         | 377        |
| internal_employee_0 | internal_employee_0/logs/sm.log                                                                                |    479           | 999        |
| internal_employee_1 | internal_employee_1/logs/sm.log                                                                                |   3893.3         | 9,606      |
| internal_employee_2 | internal_employee_2/logs/sm.log                                                                                |   3488.4         | 8,716      |
| internal_employee_3 | internal_employee_3/logs/downloads/Example(1).odt                                                              |     35.4         | 256        |
| internal_employee_3 | internal_employee_3/logs/downloads/Example.odt                                                                 |     35.4         | 256        |
| internal_employee_3 | internal_employee_3/logs/sm.log                                                                                |   3587.9         | 9,063      |
| internal_share      | internal_share/logs/audit/audit.log                                                                            |    127.1         | 732        |
| internal_share      | internal_share/logs/auth.log                                                                                   |      9.2         | 92         |
| internal_share      | internal_share/logs/auth.log.1                                                                                 |     12.3         | 124        |
| internal_share      | internal_share/logs/journal/94ffb314fce9427fa503bc72f7807ae3/system@0005d60195803429-c8be82c14312eaab.journal~ |   8192           | 159        |
| internal_share      | internal_share/logs/suricata/eve.json                                                                          | 315642           | 123,181    |
| internal_share      | internal_share/logs/suricata/fast.log                                                                          |      5.7         | 25         |
| internal_share      | internal_share/logs/suricata/log.pcap.1642684613                                                               | 256632           | 3,364,263  |
| internal_share      | internal_share/logs/suricata/stats.log                                                                         | 239726           | 3,047,908  |
| internal_share      | internal_share/logs/suricata/suricata-start.log                                                                |      1.1         | 12         |
| internal_share      | internal_share/logs/suricata/suricata.log                                                                      |    245.6         | 1,100      |
| internal_share      | internal_share/logs/syslog.1                                                                                   |      3.1         | 32         |
| internal_share      | internal_share/logs/syslog.2                                                                                   |      5.8         | 58         |
| internal_share      | internal_share/logs/syslog.3                                                                                   |      5           | 49         |
| internal_share      | internal_share/logs/syslog.4                                                                                   |     19.1         | 198        |
| intranet_server     | intranet_server/logs/apache2/access.log                                                                        |      0           | 0          |
| intranet_server     | intranet_server/logs/apache2/error.log.1                                                                       |      0.2         | 2          |
| intranet_server     | intranet_server/logs/apache2/error.log.2                                                                       |    277.9         | 3,856      |
| intranet_server     | intranet_server/logs/apache2/error.log.3                                                                       |      0.4         | 3          |
| intranet_server     | intranet_server/logs/apache2/error.log.4                                                                       |      0.1         | 1          |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access.log                                     |      0           | 0          |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access.log.1                                   |    145.9         | 601        |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access.log.2                                   |   1528.4         | 8,530      |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access.log.3                                   |    250.1         | 933        |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access.log.4                                   |    282.7         | 1,120      |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error.log                                      |      0           | 0          |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error.log.1                                    |      0.6         | 2          |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error.log.2                                    |      8.4         | 36         |
| intranet_server     | intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error.log.3                                    |      0.6         | 2          |
| intranet_server     | intranet_server/logs/apache2/other_vhosts_access.log                                                           |      0           | 0          |
| intranet_server     | intranet_server/logs/audit/audit.log                                                                           |    411           | 2,316      |
| intranet_server     | intranet_server/logs/auth.log                                                                                  |     27.6         | 272        |
| intranet_server     | intranet_server/logs/auth.log.1                                                                                |     36           | 356        |
| intranet_server     | intranet_server/logs/suricata/eve.json                                                                         | 282363           | 66,428     |
| intranet_server     | intranet_server/logs/suricata/fast.log                                                                         |      9.8         | 44         |
| intranet_server     | intranet_server/logs/suricata/log.pcap.1642684613                                                              | 335188           | 5,686,876  |
| intranet_server     | intranet_server/logs/suricata/stats.log                                                                        | 238947           | 3,041,945  |
| intranet_server     | intranet_server/logs/suricata/suricata-start.log                                                               |      1.1         | 12         |
| intranet_server     | intranet_server/logs/suricata/suricata.log                                                                     |    245.6         | 1,100      |
| intranet_server     | intranet_server/logs/syslog.1                                                                                  |     14.6         | 142        |
| intranet_server     | intranet_server/logs/syslog.2                                                                                  |     23.4         | 232        |
| intranet_server     | intranet_server/logs/syslog.3                                                                                  |     20.9         | 201        |
| intranet_server     | intranet_server/logs/syslog.4                                                                                  |     46.1         | 463        |
| mail                | mail/logs/audit/audit.log                                                                                      |   1588.2         | 7,388      |
| mail                | mail/logs/auth.log                                                                                             |     25           | 275        |
| mail                | mail/logs/auth.log.1                                                                                           |     32.6         | 360        |
| mail                | mail/logs/exim4/mainlog                                                                                        |      0.5         | 7          |
| mail                | mail/logs/exim4/mainlog.1                                                                                      |    135           | 921        |
| mail                | mail/logs/exim4/mainlog.2                                                                                      |    126.7         | 871        |
| mail                | mail/logs/exim4/mainlog.3                                                                                      |    122.6         | 835        |
| mail                | mail/logs/exim4/mainlog.4                                                                                      |    203.9         | 1,414      |
| mail                | mail/logs/horde/horde-access.log                                                                               |   9852.5         | 34,371     |
| mail                | mail/logs/horde/horde-error.log                                                                                |     18.3         | 54         |
| mail                | mail/logs/mail.info                                                                                            |    320.8         | 2,693      |
| mail                | mail/logs/mail.info.1                                                                                          |    290.6         | 2,459      |
| mail                | mail/logs/mail.log                                                                                             |    320.8         | 2,693      |
| mail                | mail/logs/mail.log.1                                                                                           |    290.6         | 2,459      |
| mail                | mail/logs/mail.warn                                                                                            |      0           | 0          |
| mail                | mail/logs/messages                                                                                             |    968.2         | 3,564      |
| mail                | mail/logs/messages.1                                                                                           |   1012.9         | 4,008      |
| mail                | mail/logs/suricata/eve.json                                                                                    |  57137.5         | 56,655     |
| mail                | mail/logs/suricata/eve.json.1                                                                                  |  73145.1         | 70,106     |
| mail                | mail/logs/suricata/fast.log                                                                                    |      2.3         | 12         |
| mail                | mail/logs/suricata/fast.log.1                                                                                  |      0           | 0          |
| mail                | mail/logs/suricata/log.pcap.1642684586                                                                         | 274076           | 2,669,308  |
| mail                | mail/logs/suricata/stats.log                                                                                   |  84928.7         | 1,111,959  |
| mail                | mail/logs/suricata/stats.log.1                                                                                 | 109628           | 1,440,165  |
| mail                | mail/logs/suricata/suricata.log                                                                                |      0.2         | 2          |
| mail                | mail/logs/suricata/suricata.log.1                                                                              |      5.3         | 41         |
| mail                | mail/logs/syslog.1                                                                                             |    771.1         | 4,120      |
| mail                | mail/logs/syslog.2                                                                                             |    769.2         | 4,338      |
| mail                | mail/logs/syslog.3                                                                                             |    558.3         | 3,454      |
| mail                | mail/logs/syslog.4                                                                                             |    766           | 4,541      |
| mail                | mail/logs/user.log                                                                                             |    968.1         | 3,563      |
| mail                | mail/logs/user.log.1                                                                                           |    986.6         | 3,691      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.auth.log                                             |    817.9         | 1,164      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.cpu.log                                              |    776.8         | 866        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.diskio.log                                           |   6083.3         | 6,919      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.filesystem.log                                       |    453.4         | 654        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.fsstat.log                                           |    132           | 218        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.load.log                                             |    492.8         | 866        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.memory.log                                           |    933.4         | 866        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.network.log                                          |   1594.3         | 2,596      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.process.log                                          |     19.8         | 10         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.process.summary.log                                  |    540.4         | 866        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.service.log                                          |  72917.4         | 89,094     |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.socket.summary.log                                   |    680.6         | 866        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.syslog.log                                           |    954.5         | 1,452      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-20-system.uptime.log                                           |     23.8         | 45         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.auth.log                                             |     36.4         | 55         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.cpu.log                                              |   1724.3         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.diskio.log                                           |  13560           | 15,360     |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.filesystem.log                                       |    998.4         | 1,440      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.fsstat.log                                           |    290.7         | 480        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.load.log                                             |   1092.9         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.memory.log                                           |   2171.6         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.network.log                                          |   3547.1         | 5,760      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.process.summary.log                                  |   1198.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.service.log                                          | 161881           | 197,761    |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.socket.summary.log                                   |   1509.3         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.syslog.log                                           |    119.1         | 180        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-21-system.uptime.log                                           |     50.8         | 96         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.auth.log                                             |     34.5         | 52         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.cpu.log                                              |   1724.4         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.diskio.log                                           |  13578.6         | 15,360     |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.filesystem.log                                       |    998.2         | 1,440      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.fsstat.log                                           |    290.7         | 480        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.load.log                                             |   1093           | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.memory.log                                           |   2176.5         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.network.log                                          |   3547.2         | 5,760      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.process.summary.log                                  |   1198.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.service.log                                          | 161890           | 197,760    |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.socket.summary.log                                   |   1509.3         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.syslog.log                                           |     33.9         | 51         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-22-system.uptime.log                                           |     50.9         | 96         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.auth.log                                             |     37.1         | 56         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.cpu.log                                              |   1724.5         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.diskio.log                                           |  13572.3         | 15,360     |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.filesystem.log                                       |    998.2         | 1,440      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.fsstat.log                                           |    290.7         | 480        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.load.log                                             |   1093.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.memory.log                                           |   2176.4         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.network.log                                          |   3549.4         | 5,760      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.process.summary.log                                  |   1198.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.service.log                                          | 161890           | 197,760    |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.socket.summary.log                                   |   1509.3         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.syslog.log                                           |     35.8         | 54         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-23-system.uptime.log                                           |     50.9         | 96         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.auth.log                                             |     35.1         | 53         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.cpu.log                                              |   1725.2         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.diskio.log                                           |  13574.5         | 15,360     |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.filesystem.log                                       |    998.2         | 1,440      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.fsstat.log                                           |    290.7         | 480        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.load.log                                             |   1093           | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.memory.log                                           |   2178.6         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.network.log                                          |   3551.7         | 5,760      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.process.summary.log                                  |   1198.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.service.log                                          | 161221           | 196,948    |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.socket.summary.log                                   |   1509.3         | 1,920      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.syslog.log                                           |     34.4         | 52         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-24-system.uptime.log                                           |     50.9         | 96         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.auth.log                                             |     35.5         | 53         |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.cpu.log                                              |    505           | 562        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.diskio.log                                           |   3974.8         | 4,496      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.filesystem.log                                       |    291.1         | 420        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.fsstat.log                                           |     84.8         | 140        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.load.log                                             |    319.9         | 562        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.memory.log                                           |    637.9         | 562        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.network.log                                          |   1039.1         | 1,686      |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.process.summary.log                                  |    350.7         | 562        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.service.log                                          |  46926           | 57,327     |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.socket.summary.log                                   |    441.8         | 562        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.syslog.log                                           |    102.5         | 157        |
| monitoring          | monitoring/logs/logstash/internal-share/2022-01-25-system.uptime.log                                           |     14.8         | 28         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.auth.log                                            |    631.9         | 895        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.cpu.log                                             |    777.4         | 866        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.diskio.log                                          |   6102           | 6,919      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.filesystem.log                                      |    455.5         | 654        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.fsstat.log                                          |    132.7         | 218        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.load.log                                            |    495.4         | 866        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.memory.log                                          |    980.3         | 866        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.network.log                                         |   1602.1         | 2,596      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.process.log                                         |     19.5         | 10         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.process.summary.log                                 |    542.9         | 866        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.service.log                                         |  73765.6         | 89,900     |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.socket.summary.log                                  |    682.5         | 866        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.syslog.log                                          |   1165.8         | 1,755      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-20-system.uptime.log                                          |     23.9         | 45         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.auth.log                                            |    110.1         | 165        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.cpu.log                                             |   1725           | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.diskio.log                                          |  13580.5         | 15,360     |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.filesystem.log                                      |   1002.5         | 1,440      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.fsstat.log                                          |    292.1         | 480        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.load.log                                            |   1098.2         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.memory.log                                          |   2185.6         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.network.log                                         |   3554.2         | 5,760      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.process.summary.log                                 |   1203.8         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.service.log                                         | 163874           | 199,199    |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.socket.summary.log                                  |   1512.9         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.syslog.log                                          |    270.9         | 406        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-21-system.uptime.log                                          |     51.1         | 96         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.auth.log                                            |     98.8         | 148        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.cpu.log                                             |   1724.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.diskio.log                                          |  13605.6         | 15,360     |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.filesystem.log                                      |   1002.3         | 1,440      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.fsstat.log                                          |    292.1         | 480        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.load.log                                            |   1098.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.memory.log                                          |   2188.4         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.network.log                                         |   3554.6         | 5,760      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.process.summary.log                                 |   1203.8         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.service.log                                         | 164342           | 199,680    |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.socket.summary.log                                  |   1513.2         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.syslog.log                                          |    133.5         | 199        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-22-system.uptime.log                                          |     51.2         | 96         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.auth.log                                            |    105.3         | 158        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.cpu.log                                             |   1723           | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.diskio.log                                          |  13607.2         | 15,360     |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.filesystem.log                                      |   1002.3         | 1,440      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.fsstat.log                                          |    292.1         | 480        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.load.log                                            |   1098.2         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.memory.log                                          |   2190           | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.network.log                                         |   3555.7         | 5,760      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.process.summary.log                                 |   1203.8         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.service.log                                         | 164333           | 199,670    |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.socket.summary.log                                  |   1513.2         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.syslog.log                                          |    153.1         | 229        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-23-system.uptime.log                                          |     51.2         | 96         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.auth.log                                            |    104.7         | 157        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.cpu.log                                             |   1723.7         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.diskio.log                                          |  13596.9         | 15,360     |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.filesystem.log                                      |   1002.4         | 1,440      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.fsstat.log                                          |    292.1         | 480        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.load.log                                            |   1098.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.memory.log                                          |   2189.9         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.network.log                                         |   3555.8         | 5,760      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.process.summary.log                                 |   1205.3         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.service.log                                         | 164530           | 199,680    |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.socket.summary.log                                  |   1518.1         | 1,920      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.syslog.log                                          |    136.5         | 204        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-24-system.uptime.log                                          |     51.2         | 96         |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.auth.log                                            |     77.3         | 115        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.cpu.log                                             |    506           | 563        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.diskio.log                                          |   3983.1         | 4,504      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.filesystem.log                                      |    292.3         | 420        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.fsstat.log                                          |     85.2         | 140        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.load.log                                            |    322           | 563        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.memory.log                                          |    642.1         | 563        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.network.log                                         |   1042.6         | 1,689      |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.process.summary.log                                 |    353.5         | 563        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.service.log                                         |  48250.5         | 58,559     |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.socket.summary.log                                  |    445.4         | 563        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.syslog.log                                          |    224.1         | 341        |
| monitoring          | monitoring/logs/logstash/intranet-server/2022-01-25-system.uptime.log                                          |     14.9         | 28         |
| monitoring          | monitoring/logs/logstash/logstash-deprecation-2022-01-20-1.log                                                 |     22.2         | 62         |
| monitoring          | monitoring/logs/logstash/logstash-deprecation-2022-01-21-1.log                                                 |     45.2         | 125        |
| monitoring          | monitoring/logs/logstash/logstash-deprecation-2022-01-22-1.log                                                 |     41.9         | 116        |
| monitoring          | monitoring/logs/logstash/logstash-deprecation-2022-01-23-1.log                                                 |     44.1         | 122        |
| monitoring          | monitoring/logs/logstash/logstash-deprecation-2022-01-24-1.log                                                 |     43.7         | 121        |
| monitoring          | monitoring/logs/logstash/logstash-deprecation.log                                                              |     14.1         | 39         |
| monitoring          | monitoring/logs/logstash/logstash-json.log                                                                     |      0           | 0          |
| monitoring          | monitoring/logs/logstash/logstash-plain-2022-01-20-1.log                                                       |   6257.7         | 29,844     |
| monitoring          | monitoring/logs/logstash/logstash-plain-2022-01-21-1.log                                                       |  13869.6         | 66,139     |
| monitoring          | monitoring/logs/logstash/logstash-plain-2022-01-22-1.log                                                       |  13861.1         | 66,098     |
| monitoring          | monitoring/logs/logstash/logstash-plain-2022-01-23-1.log                                                       |  13866.5         | 66,124     |
| monitoring          | monitoring/logs/logstash/logstash-plain-2022-01-24-1.log                                                       |  13869.8         | 66,140     |
| monitoring          | monitoring/logs/logstash/logstash-plain.log                                                                    |   4059.1         | 19,356     |
| monitoring          | monitoring/logs/logstash/logstash-slowlog-json.log                                                             |      0           | 0          |
| monitoring          | monitoring/logs/logstash/logstash-slowlog-plain.log                                                            |      0           | 0          |
| morris_mail         | morris_mail/logs/auth.log                                                                                      |     31.3         | 320        |
| morris_mail         | morris_mail/logs/auth.log.1                                                                                    |     88.5         | 779        |
| morris_mail         | morris_mail/logs/exim4/mainlog                                                                                 |      0.1         | 2          |
| morris_mail         | morris_mail/logs/exim4/mainlog.1                                                                               |     64.9         | 406        |
| morris_mail         | morris_mail/logs/exim4/mainlog.2                                                                               |     61.8         | 422        |
| morris_mail         | morris_mail/logs/exim4/mainlog.3                                                                               |     57.4         | 387        |
| morris_mail         | morris_mail/logs/exim4/mainlog.4                                                                               |     89.3         | 625        |
| morris_mail         | morris_mail/logs/horde/horde-access.log                                                                        |   2244.9         | 6,879      |
| morris_mail         | morris_mail/logs/horde/horde-error.log                                                                         |      0           | 0          |
| morris_mail         | morris_mail/logs/mail.info                                                                                     |    108.3         | 840        |
| morris_mail         | morris_mail/logs/mail.info.1                                                                                   |    120           | 938        |
| morris_mail         | morris_mail/logs/mail.log                                                                                      |    108.3         | 840        |
| morris_mail         | morris_mail/logs/mail.log.1                                                                                    |    120           | 938        |
| morris_mail         | morris_mail/logs/mail.warn                                                                                     |      0           | 0          |
| morris_mail         | morris_mail/logs/mail.warn.1                                                                                   |      0.4         | 4          |
| morris_mail         | morris_mail/logs/messages                                                                                      |     30.6         | 160        |
| morris_mail         | morris_mail/logs/messages.1                                                                                    |     73.5         | 552        |
| morris_mail         | morris_mail/logs/syslog                                                                                        |     25           | 306        |
| morris_mail         | morris_mail/logs/syslog.1                                                                                      |    117.8         | 909        |
| morris_mail         | morris_mail/logs/syslog.2                                                                                      |    114.2         | 888        |
| morris_mail         | morris_mail/logs/syslog.3                                                                                      |    103.3         | 804        |
| morris_mail         | morris_mail/logs/syslog.4                                                                                      |    305.7         | 2,709      |
| morris_mail         | morris_mail/logs/user.log                                                                                      |     30.5         | 159        |
| morris_mail         | morris_mail/logs/user.log.1                                                                                    |     45.8         | 237        |
| remote_employee_0   | remote_employee_0/logs/sm.log                                                                                  |   5032           | 12,797     |
| remote_employee_1   | remote_employee_1/logs/sm.log                                                                                  |   3805.2         | 9,723      |
| remote_employee_2   | remote_employee_2/logs/sm.log                                                                                  |    740.9         | 1,873      |
| vpn                 | vpn/logs/audit/audit.log                                                                                       |    126           | 726        |
| vpn                 | vpn/logs/auth.log                                                                                              |      8.1         | 92         |
| vpn                 | vpn/logs/auth.log.1                                                                                            |     11           | 124        |
| vpn                 | vpn/logs/openvpn.log                                                                                           |    530.7         | 5,537      |
| vpn                 | vpn/logs/suricata/eve.json                                                                                     | 388680           | 267,061    |
| vpn                 | vpn/logs/suricata/fast.log                                                                                     |    412.4         | 2,089      |
| vpn                 | vpn/logs/suricata/log.pcap.1642684648                                                                          |      1.00969e+06 | 8,421,682  |
| vpn                 | vpn/logs/suricata/log.pcap.1642964618                                                                          | 424829           | 3,549,710  |
| vpn                 | vpn/logs/suricata/stats.log                                                                                    | 253020           | 3,206,910  |
| vpn                 | vpn/logs/suricata/suricata-start.log                                                                           |      1.1         | 12         |
| vpn                 | vpn/logs/suricata/suricata.log                                                                                 |    245.6         | 1,100      |
| vpn                 | vpn/logs/syslog.1                                                                                              |      2.9         | 34         |
| vpn                 | vpn/logs/syslog.2                                                                                              |      7.9         | 90         |
| vpn                 | vpn/logs/syslog.3                                                                                              |      4.3         | 47         |
| vpn                 | vpn/logs/syslog.4                                                                                              |     16.6         | 193        |
| webserver           | webserver/logs/apache2/access.log                                                                              |      0           | 0          |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-access.log                                              |      0           | 0          |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-access.log.1                                            |   1251.4         | 5,515      |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-access.log.2                                            |   1617.6         | 6,869      |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-access.log.3                                            |   1807.4         | 7,541      |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-access.log.4                                            |   1747.5         | 7,366      |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-error.log                                               |      0           | 0          |
| webserver           | webserver/logs/apache2/cloud.smith.russellmitchell.com-error.log.1                                             |      0.2         | 1          |
| webserver           | webserver/logs/apache2/error.log.1                                                                             |      0.3         | 2          |
| webserver           | webserver/logs/apache2/error.log.2                                                                             |      0.4         | 3          |
| webserver           | webserver/logs/apache2/error.log.3                                                                             |      0.4         | 3          |
| webserver           | webserver/logs/apache2/error.log.4                                                                             |      0.1         | 1          |
| webserver           | webserver/logs/apache2/mail.smith.russellmitchell.com-access.log                                               |      0           | 0          |
| webserver           | webserver/logs/apache2/mail.smith.russellmitchell.com-access.log.1                                             |   2688.7         | 9,488      |
| webserver           | webserver/logs/apache2/mail.smith.russellmitchell.com-access.log.2                                             |   2537           | 8,783      |
| webserver           | webserver/logs/apache2/mail.smith.russellmitchell.com-access.log.3                                             |   2280           | 8,025      |
| webserver           | webserver/logs/apache2/mail.smith.russellmitchell.com-access.log.4                                             |   2344.3         | 8,215      |
| webserver           | webserver/logs/apache2/mail.smith.russellmitchell.com-error.log                                                |      0           | 0          |
| webserver           | webserver/logs/apache2/other_vhosts_access.log                                                                 |      0           | 0          |
| webserver           | webserver/logs/apache2/proxy-access.log                                                                        |      0           | 0          |
| webserver           | webserver/logs/apache2/proxy-access.log.1                                                                      |     93.7         | 772        |
| webserver           | webserver/logs/apache2/proxy-access.log.2                                                                      |     97           | 818        |
| webserver           | webserver/logs/apache2/proxy-access.log.3                                                                      |     78.2         | 653        |
| webserver           | webserver/logs/apache2/proxy-access.log.4                                                                      |     72.5         | 608        |
| webserver           | webserver/logs/apache2/proxy-error.log.1                                                                       |      0.2         | 1          |
| webserver           | webserver/logs/apache2/proxy-error.log.2                                                                       |      4           | 25         |
| webserver           | webserver/logs/apache2/proxy-error.log.3                                                                       |      0.2         | 1          |
| webserver           | webserver/logs/audit/audit.log                                                                                 |    400.6         | 2,264      |
| webserver           | webserver/logs/auth.log                                                                                        |     24.6         | 258        |
| webserver           | webserver/logs/auth.log.1                                                                                      |     32.4         | 342        |
| webserver           | webserver/logs/suricata/eve.json                                                                               | 353029           | 173,842    |
| webserver           | webserver/logs/suricata/fast.log                                                                               |    489.8         | 2,507      |
| webserver           | webserver/logs/suricata/log.pcap.1642684648                                                                    |      1.00786e+06 | 9,934,779  |
| webserver           | webserver/logs/suricata/log.pcap.1643023053                                                                    | 184193           | 1,854,292  |
| webserver           | webserver/logs/suricata/stats.log                                                                              | 231310           | 2,929,190  |
| webserver           | webserver/logs/suricata/suricata-start.log                                                                     |      1.1         | 12         |
| webserver           | webserver/logs/suricata/suricata.log                                                                           |    245.6         | 1,100      |
| webserver           | webserver/logs/syslog.1                                                                                        |     13.3         | 137        |
| webserver           | webserver/logs/syslog.2                                                                                        |     19.3         | 197        |
| webserver           | webserver/logs/syslog.3                                                                                        |     19.9         | 203        |
| webserver           | webserver/logs/syslog.4                                                                                        |     38.1         | 397        |


**Total:** 455 log files, 13660.0 MB, 128,036,258 lines


## 2. Scenario Comparison

## Scenario Comparison

The `environment/datasets/` directory defines 3 attack scenarios that can be generated from the same raw log data.

### Summary

| Aspect | scenario (full) | scenario1 (no exfil) | scenario2 (exfil only) |
|--------|-----------------|---------------------|----------------------|
| Foothold attack | Yes | Yes | No |
| Escalation | Yes | Yes | No |
| DNS exfiltration | Yes | No | Yes |
| Attacker state machine | Yes | Yes | No |
| DNSteal log collected | Yes | No | Yes |
| CPU monitoring | Yes | Yes | No |
| Excluded hosts | mgmthost | mgmthost | monitoring, mgmthost, internal_employee_6 |
| Labeling rules | 6 rules | 5 rules | 2 rules |

### Labeling Rules Per Scenario

| Rule File | scenario | scenario1 | scenario2 |
|-----------|----------|-----------|-----------|
| 0_auth.yaml | Yes | Yes | - |
| apache.yaml | Yes | Yes | - |
| audit.yaml | Yes | Yes | Yes |
| dnsmasq.yaml | Yes | - | Yes |
| monitoring.yaml | Yes | Yes | - |
| openvpn.yaml | Yes | Yes | - |

### Attack Phases Defined

| Phase | scenario | scenario1 | scenario2 |
|-------|----------|-----------|-----------|
| dnsteal | Yes | - | Yes |
| escalate | Yes | Yes | - |
| foothold | Yes | Yes | - |
| partial_exfil_stop | Yes | - | Yes |

### Impact on Project Data

Our processed dataset uses the **full "scenario"** configuration. This is confirmed by comparing
`processing/process.yaml` (root) with `environment/datasets/scenario/processing/process.yaml` -- they are identical.

**What this means for us:**
- We have labels for ALL attack phases: foothold, escalation, AND exfiltration
- All 6 labeling rules are active, producing labels across 8 log files on 5 hosts
- The attacker state machine log captures the full kill chain
- CPU monitoring data captures the password-cracking CPU spike
- DNS exfiltration labels identify the 54K+ dnsteal queries in dnsmasq.log

**If we had scenario1** (no exfiltration):
- We would lose ~54K labeled DNS lines (the dnsteal exfiltration labels)
- dnsmasq.log would have NO attack labels at all
- The `dns_events` table would contain only normal traffic with no attack correlation

**If we had scenario2** (exfiltration only):
- We would lose ALL web attack labels (Apache, auth, VPN)
- Only audit.yaml and dnsmasq.yaml rules would be active
- The entire foothold/escalation narrative would be invisible
- Monitoring host excluded entirely -- no CPU anomaly detection possible


## 3. Per-Log-Type Deep Profile

Parsing all 8 labeled log files and their corresponding label files...



### DNS (dnsmasq) -- Field-Level Profile

**Rows:** 275,900 | **Columns:** 10

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-21 00:00:09 to 2022-01-24 23:58:27 (span: 3 days 23:58:18)

| Column          | Type           |   Non-Null |   Null |   Unique | Min                 | Max                 | Mean     | Top Values                                                                                                   |
|:----------------|:---------------|-----------:|-------:|---------:|:--------------------|:--------------------|:---------|:-------------------------------------------------------------------------------------------------------------|
| line_number     | int64          |     275900 |      0 |   275900 | 1                   | 275900              | 137950.5 | 1 (1); 2 (1); 3 (1) ... (275900 unique)                                                                      |
| action          | str            |     275900 |      0 |        6 |                     |                     |          | reply (99406); query (81277); forwarded (57960); cached (25763); nameserver (11493)                          |
| query_type      | str            |      81277 | 194623 |        6 |                     |                     |          | A (40275); AAAA (38967); PTR (1055); TXT (582); MX (202)                                                     |
| domain          | str            |     275900 |      0 |    21143 |                     |                     |          | e6410.d.akamaiedge.net (21794); 127.0.0.1 (11493); eus-tivan.naver.com.akadns.net (11390) ... (21143 unique) |
| client_ip       | str            |      81277 | 194623 |       15 |                     |                     |          | 10.143.1.78 (29956); 10.143.0.103 (17765); 172.19.131.174 (11036); 172.19.130.4 (7636); 10.143.2.91 (7532)   |
| extra_ip        | str            |     183129 |  92771 |     6324 |                     |                     |          | 192.168.231.254 (45731); NODATA-IPv6 (33745); <CNAME> (23810) ... (6324 unique)                              |
| is_exfiltration | bool           |     275900 |      0 |        2 | False               | True                | 0.1923   | False (222846); True (53054)                                                                                 |
| timestamp       | datetime64[us] |     275900 |      0 |    27302 | 2022-01-21 00:00:09 | 2022-01-24 23:58:27 |          | 2022-01-24 03:01:21 (414); 2022-01-21 10:45:45 (338); 2022-01-21 10:09:39 (330) ... (27302 unique)           |


### DNS (dnsmasq) -- Sample Data (first 5 rows)

```
   line_number    timestamp_raw     action query_type                                                       domain     client_ip         extra_ip  is_exfiltration  parse_error           timestamp
0            1  Jan 21 00:00:09      query          A  3x6-.596-.IunWTzebVlyAhhHj*ZfWjOBun1zAf*Wgpq-.YarqcF7oov...  10.143.0.103              NaN             True        False 2022-01-21 00:00:09
1            2  Jan 21 00:00:09  forwarded        NaN  3x6-.596-.IunWTzebVlyAhhHj*ZfWjOBun1zAf*Wgpq-.YarqcF7oov...           NaN  192.168.231.254             True        False 2022-01-21 00:00:09
2            3  Jan 21 00:00:09      reply        NaN  3x6-.596-.IunWTzebVlyAhhHj*ZfWjOBun1zAf*Wgpq-.YarqcF7oov...           NaN  195.128.194.168             True        False 2022-01-21 00:00:09
3            4  Jan 21 00:00:31      query          A  3x6-.597-.L**fA/ib4pGEIb5*uJ223L5A/pWGilEyrR-.u9lQ3wFEj1...  10.143.0.103              NaN             True        False 2022-01-21 00:00:31
4            5  Jan 21 00:00:31  forwarded        NaN  3x6-.597-.L**fA/ib4pGEIb5*uJ223L5A/pWGilEyrR-.u9lQ3wFEj1...           NaN  192.168.231.254             True        False 2022-01-21 00:00:31
```


### Apache Access (intranet) -- Field-Level Profile

**Rows:** 8,530 | **Columns:** 14

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-23 06:36:13+00:00 to 2022-01-24 04:37:25+00:00 (span: 0 days 22:01:12)

| Column       | Type                |   Non-Null |   Null |   Unique | Min                       | Max                       | Mean   | Top Values                                                                                                                                                                                                                                                                                                                                                                                                              |
|:-------------|:--------------------|-----------:|-------:|---------:|:--------------------------|:--------------------------|:-------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| line_number  | int64               |       8530 |      0 |     8530 | 1                         | 8530                      | 4265.5 | 1 (1); 2 (1); 3 (1) ... (8530 unique)                                                                                                                                                                                                                                                                                                                                                                                   |
| client_ip    | str                 |       8530 |      0 |        6 |                           |                           |        | 172.19.131.174 (8027); 10.143.2.25 (206); 10.143.2.91 (137); 10.143.3.65 (111); ::1 (30)                                                                                                                                                                                                                                                                                                                                |
| method       | str                 |       8530 |      0 |        5 |                           |                           |        | GET (5206); HEAD (3169); POST (111); OPTIONS (30); - (14)                                                                                                                                                                                                                                                                                                                                                               |
| path         | str                 |       8516 |     14 |     7561 |                           |                           |        | / (222); /wp-admin/admin-ajax.php (92); /wp-includes/css/dist/block-library/style.min.css (48) ... (7561 unique)                                                                                                                                                                                                                                                                                                        |
| query_string | str                 |        623 |   7907 |      158 |                           |                           |        | ver=5.8.3 (182); ver=1.5.2 (134); ver=7.0.4 (72) ... (158 unique)                                                                                                                                                                                                                                                                                                                                                       |
| protocol     | str                 |       8516 |     14 |        2 |                           |                           |        | HTTP/1.1 (8482); HTTP/1.0 (34)                                                                                                                                                                                                                                                                                                                                                                                          |
| status_code  | int64               |       8530 |      0 |        8 | 200                       | 500                       | 383.4  | 404 (7641); 200 (857); 408 (14); 403 (8); 301 (6)                                                                                                                                                                                                                                                                                                                                                                       |
| bytes_sent   | int64               |       8530 |      0 |      197 | 0                         | 570058                    | 3662.9 | 363 (4360); 146 (3000); 335 (99) ... (197 unique)                                                                                                                                                                                                                                                                                                                                                                       |
| referer      | str                 |       3851 |   4679 |        5 |                           |                           |        | https://intranet.smith.russellmitchell.com (3186); https://intranet.smith.russellmitchell.com/?p=5 (415); http://intranet.smith.russellmitchell.com/ (134); https://intranet.smith.russellmitchell.com/wp-content/plugins/wpdiscuz/assets/third-party/font-awesome-5.13.0/css/fa.min.css?ver=7.0.4 (72); https://intranet.smith.russellmitchell.com/wp-content/plugins/wpdiscuz/themes/default/style.css?ver=7.0.4 (44) |
| user_agent   | str                 |       8510 |     20 |        8 |                           |                           |        | Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) (4462); WPScan v3.8.20 (https://wpscan.com/wordpress-security-scanner) (3186); Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/97.0.4692.71 Safari/537.36 (433); Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0 (338); python-requests/2.27.1 (36)                                               |
| timestamp    | datetime64[us, UTC] |       8530 |      0 |      321 | 2022-01-23 06:36:13+00:00 | 2022-01-24 04:37:25+00:00 |        | 2022-01-24 03:57:30+00:00 (394); 2022-01-24 03:57:28+00:00 (382); 2022-01-24 03:57:38+00:00 (375) ... (321 unique)                                                                                                                                                                                                                                                                                                      |


### Apache Access (intranet) -- Sample Data (first 5 rows)

```
   line_number    client_ip               timestamp_raw method                                                 path query_string  protocol  status_code  bytes_sent                                     referer                                                   user_agent  parse_error                 timestamp
0            1  10.143.2.91  23/Jan/2022:06:36:13 +0000    GET                                                    /          NaN  HTTP/1.1          200        6203                                         NaN  Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/2...        False 2022-01-23 06:36:13+00:00
1            2  10.143.2.91  23/Jan/2022:06:36:14 +0000    GET    /wp-includes/css/dist/block-library/style.min.css    ver=5.8.3  HTTP/1.1          200       10846  http://intranet.smith.russellmitchell.com/  Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/2...        False 2022-01-23 06:36:14+00:00
2            3  10.143.2.91  23/Jan/2022:06:36:14 +0000    GET                      /wp-includes/js/wp-embed.min.js    ver=5.8.3  HTTP/1.1          200        1099  http://intranet.smith.russellmitchell.com/  Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/2...        False 2022-01-23 06:36:14+00:00
3            4  10.143.2.91  23/Jan/2022:06:36:14 +0000    GET        /wp-content/themes/go/dist/js/frontend.min.js    ver=1.5.2  HTTP/1.1          200        2916  http://intranet.smith.russellmitchell.com/  Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/2...        False 2022-01-23 06:36:14+00:00
4            5  10.143.2.91  23/Jan/2022:06:36:14 +0000    GET  /wp-content/themes/go/dist/css/style-shared.min.css    ver=1.5.2  HTTP/1.1          200       23204  http://intranet.smith.russellmitchell.com/  Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/2...        False 2022-01-23 06:36:14+00:00
```


### Apache Error (intranet) -- Field-Level Profile

**Rows:** 36 | **Columns:** 10

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-24 03:57:26.696483 to 2022-01-24 03:58:09.826189 (span: 0 days 00:00:43.129706)

| Column      | Type           |   Non-Null |   Null |   Unique | Min                        | Max                        | Mean    | Top Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:------------|:---------------|-----------:|-------:|---------:|:---------------------------|:---------------------------|:--------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| line_number | int64          |         36 |      0 |       36 | 1                          | 36                         | 18.5    | 1 (1); 2 (1); 3 (1); 4 (1); 5 (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| module      | str            |         36 |      0 |        4 |                            |                            |         | php7 (15); negotiation (13); authz_core (7); autoindex (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| level       | str            |         36 |      0 |        1 |                            |                            |         | error (36)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| pid         | int64          |         36 |      0 |       10 | 23059                      | 27752                      | 25134.4 | 25026 (11); 25711 (7); 23059 (5); 25876 (3); 25705 (3)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| client_ip   | str            |         36 |      0 |        1 |                            |                            |         | 172.19.131.174 (36)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| client      | str            |         36 |      0 |       16 |                            |                            |         | 172.19.131.174:36158 (11); 172.19.131.174:36072 (6); 172.19.131.174:36166 (3); 172.19.131.174:36110 (2); 172.19.131.174:36218 (2)                                                                                                                                                                                                                                                                                                                                                                                                             |
| message     | str            |         36 |      0 |       36 |                            |                            |         | AH01630: client denied by server configuration: /var/www/intranet.smith.russellmitchell.com/.hta (1); AH01630: client denied by server configuration: /var/www/intranet.smith.russellmitchell.com/.hta_ (1); AH01630: client denied by server configuration: /var/www/intranet.smith.russellmitchell.com/.htaccess (1); AH01630: client denied by server configuration: /var/www/intranet.smith.russellmitchell.com/.htaccess_ (1); AH01630: client denied by server configuration: /var/www/intranet.smith.russellmitchell.com/.htpasswd (1) |
| timestamp   | datetime64[us] |         36 |      0 |       36 | 2022-01-24 03:57:26.696483 | 2022-01-24 03:58:09.826189 |         | 2022-01-24 03:57:26.696483 (1); 2022-01-24 03:57:26.698653 (1); 2022-01-24 03:57:26.700701 (1); 2022-01-24 03:57:26.702901 (1); 2022-01-24 03:57:26.704945 (1)                                                                                                                                                                                                                                                                                                                                                                                |


### Apache Error (intranet) -- Sample Data (first 5 rows)

```
   line_number                    timestamp_raw      module  level    pid       client_ip                client                                                      message  parse_error                  timestamp
0            1  Mon Jan 24 03:57:26.696483 2022  authz_core  error  25711  172.19.131.174  172.19.131.174:36072  AH01630: client denied by server configuration: /var/www...        False 2022-01-24 03:57:26.696483
1            2  Mon Jan 24 03:57:26.698653 2022  authz_core  error  25711  172.19.131.174  172.19.131.174:36072  AH01630: client denied by server configuration: /var/www...        False 2022-01-24 03:57:26.698653
2            3  Mon Jan 24 03:57:26.700701 2022  authz_core  error  25711  172.19.131.174  172.19.131.174:36072  AH01630: client denied by server configuration: /var/www...        False 2022-01-24 03:57:26.700701
3            4  Mon Jan 24 03:57:26.702901 2022  authz_core  error  25711  172.19.131.174  172.19.131.174:36072  AH01630: client denied by server configuration: /var/www...        False 2022-01-24 03:57:26.702901
4            5  Mon Jan 24 03:57:26.704945 2022  authz_core  error  25711  172.19.131.174  172.19.131.174:36072  AH01630: client denied by server configuration: /var/www...        False 2022-01-24 03:57:26.704945
```


### Audit Log (intranet) -- Field-Level Profile

**Rows:** 2,316 | **Columns:** 19

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-21 00:09:01.072000027+00:00 to 2022-01-24 23:39:13.266000032+00:00 (span: 3 days 23:30:12.194000005)

| Column       | Type                |   Non-Null |   Null |   Unique | Min                                 | Max                                 | Mean            | Top Values                                                                                                                                  |
|:-------------|:--------------------|-----------:|-------:|---------:|:------------------------------------|:------------------------------------|:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| line_number  | int64               |       2316 |      0 |     2316 | 1                                   | 2316                                | 1158.5          | 1 (1); 2 (1); 3 (1) ... (2316 unique)                                                                                                       |
| event_type   | str                 |       2316 |      0 |       15 |                                     |                                     |                 | CRED_ACQ (308); USER_START (306); USER_ACCT (305); LOGIN (304); CRED_DISP (302)                                                             |
| audit_serial | int64               |       2316 |      0 |     2308 | 375                                 | 2682                                | 1525.1          | 529 (3); 530 (3); 531 (3) ... (2308 unique)                                                                                                 |
| pid          | float64             |       2312 |      4 |      312 | 1.0                                 | 31519.0                             | 17239.7751      | 1.0 (471); 23662.0 (8); 14362.0 (7) ... (312 unique)                                                                                        |
| uid          | float64             |       2308 |      8 |        3 | 0.0                                 | 1002.0                              | 0.4913          | 0.0 (2303); 33.0 (4); 1002.0 (1)                                                                                                            |
| auid         | float64             |       2308 |      8 |        3 | 0.0                                 | 4294967295.0                        | 2032107586.7366 | 0.0 (1192); 4294967295.0 (1092); 1002.0 (24)                                                                                                |
| ses          | str                 |       2308 |      8 |      306 |                                     |                                     |                 | 4294967295 (1092); 100 (6); 111 (6) ... (306 unique)                                                                                        |
| acct         | str                 |       1525 |    791 |        2 |                                     |                                     |                 | root (1494); jhall (31)                                                                                                                     |
| exe          | str                 |       2003 |    313 |        6 |                                     |                                     |                 | /usr/sbin/cron (1490); /lib/systemd/systemd (480); /usr/sbin/sshd (21); /sbin/apparmor_parser (4); /bin/su (4)                              |
| op           | str                 |       1528 |    788 |        6 |                                     |                                     |                 | PAM:setcred (611); PAM:session_open (306); PAM:accounting (305); PAM:session_close (302); login (3)                                         |
| result       | str                 |       2304 |     12 |        2 |                                     |                                     |                 | success (2000); 1 (304)                                                                                                                     |
| terminal     | str                 |       2000 |    316 |        6 |                                     |                                     |                 | cron (1490); ? (480); ssh (18); /dev/pts/1 (8); /dev/pts/0 (3)                                                                              |
| hostname     | str                 |       1999 |    317 |        2 |                                     |                                     |                 | ? (1978); 172.19.131.174 (21)                                                                                                               |
| addr         | str                 |       1999 |    317 |        2 |                                     |                                     |                 | ? (1978); 172.19.131.174 (21)                                                                                                               |
| unit         | object              |          0 |   2316 |        0 |                                     |                                     |                 |                                                                                                                                             |
| comm         | str                 |          8 |   2308 |        1 |                                     |                                     |                 | apparmor_parser (8)                                                                                                                         |
| timestamp    | datetime64[ns, UTC] |       2316 |      0 |     1272 | 2022-01-21 00:09:01.072000027+00:00 | 2022-01-24 23:39:13.266000032+00:00 |                 | 2022-01-21 06:29:42.132999897+00:00 (6); 2022-01-21 04:17:01.482000113+00:00 (4); 2022-01-21 07:07:01.059000015+00:00 (4) ... (1272 unique) |


### Audit Log (intranet) -- Sample Data (first 5 rows)

```
   line_number  event_type  timestamp_epoch  audit_serial      pid  uid          auid         ses  acct             exe                op   result terminal hostname addr  unit comm  parse_error                           timestamp
0            1   USER_ACCT     1.642724e+09           375  10125.0  0.0  4.294967e+09  4294967295  root  /usr/sbin/cron    PAM:accounting  success     cron        ?    ?  None  NaN        False 2022-01-21 00:09:01.072000027+00:00
1            2    CRED_ACQ     1.642724e+09           376  10125.0  0.0  4.294967e+09  4294967295  root  /usr/sbin/cron       PAM:setcred  success     cron        ?    ?  None  NaN        False 2022-01-21 00:09:01.072000027+00:00
2            3       LOGIN     1.642724e+09           377  10125.0  0.0  0.000000e+00          65   NaN             NaN               NaN        1      NaN      NaN  NaN  None  NaN        False 2022-01-21 00:09:01.075999975+00:00
3            4  USER_START     1.642724e+09           378  10125.0  0.0  0.000000e+00          65  root  /usr/sbin/cron  PAM:session_open  success     cron        ?    ?  None  NaN        False 2022-01-21 00:09:01.079999924+00:00
4            5   CRED_DISP     1.642724e+09           379  10125.0  0.0  0.000000e+00          65  root  /usr/sbin/cron       PAM:setcred  success     cron        ?    ?  None  NaN        False 2022-01-21 00:09:01.084000111+00:00
```


### Auth Log (intranet) -- Field-Level Profile

**Rows:** 272 | **Columns:** 10

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-23 06:25:05 to 2022-01-24 23:39:01 (span: 1 days 17:13:56)

| Column      | Type           |   Non-Null |   Null |   Unique | Min                 | Max                 | Mean       | Top Values                                                                                                                                                                                                                                                                                                                                           |
|:------------|:---------------|-----------:|-------:|---------:|:--------------------|:--------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| line_number | int64          |        272 |      0 |      272 | 1                   | 272                 | 136.5      | 1 (1); 2 (1); 3 (1) ... (272 unique)                                                                                                                                                                                                                                                                                                                 |
| hostname    | str            |        272 |      0 |        1 |                     |                     |            | intranet-server (272)                                                                                                                                                                                                                                                                                                                                |
| service     | str            |        272 |      0 |        6 |                     |                     |            | CRON (257); sshd (4); sudo (4); systemd-logind (3); su (3)                                                                                                                                                                                                                                                                                           |
| pid         | float64        |        267 |      5 |      134 | 957.0               | 31519.0             | 27066.5581 | 957.0 (3); 27950.0 (3); 23064.0 (2) ... (134 unique)                                                                                                                                                                                                                                                                                                 |
| message     | str            |        272 |      0 |       17 |                     |                     |            | pam_unix(cron:session): session closed for user root (129); pam_unix(cron:session): session opened for user root by (uid=0) (128); pam_unix(sshd:session): session closed for user jhall (1); Removed session 111. (1); Accepted publickey for jhall from 172.19.131.174 port 49828 ssh2: RSA SHA256:8wFbiaYPevKS/wYKnePO20v0iymTcrRh4Kr+1uRS1UM (1) |
| username    | str            |        264 |      8 |        2 |                     |                     |            | root (259); jhall (5)                                                                                                                                                                                                                                                                                                                                |
| action      | str            |        272 |      0 |        5 |                     |                     |            | session_open (132); session_close (131); other (7); auth_success (1); su_success (1)                                                                                                                                                                                                                                                                 |
| timestamp   | datetime64[us] |        272 |      0 |      139 | 2022-01-23 06:25:05 | 2022-01-24 23:39:01 |            | 2022-01-24 04:37:40 (4); 2022-01-24 04:38:06 (3); 2022-01-23 06:39:01 (2) ... (139 unique)                                                                                                                                                                                                                                                           |


### Auth Log (intranet) -- Sample Data (first 5 rows)

```
   line_number    timestamp_raw         hostname service      pid                                                      message username         action  parse_error           timestamp
0            1  Jan 23 06:25:05  intranet-server    CRON  22883.0         pam_unix(cron:session): session closed for user root     root  session_close        False 2022-01-23 06:25:05
1            2  Jan 23 06:39:01  intranet-server    CRON  23064.0  pam_unix(cron:session): session opened for user root by ...     root   session_open        False 2022-01-23 06:39:01
2            3  Jan 23 06:39:01  intranet-server    CRON  23064.0         pam_unix(cron:session): session closed for user root     root  session_close        False 2022-01-23 06:39:01
3            4  Jan 23 06:47:01  intranet-server    CRON  23137.0  pam_unix(cron:session): session opened for user root by ...     root   session_open        False 2022-01-23 06:47:01
4            5  Jan 23 06:47:02  intranet-server    CRON  23137.0         pam_unix(cron:session): session closed for user root     root  session_close        False 2022-01-23 06:47:02
```


### OpenVPN -- Field-Level Profile

**Rows:** 5,537 | **Columns:** 9

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-21 00:09:11 to 2022-01-24 23:12:27 (span: 3 days 23:03:16)

| Column      | Type           |   Non-Null |   Null |   Unique | Min                 | Max                 | Mean       | Top Values                                                                                                                                                                                                                                                               |
|:------------|:---------------|-----------:|-------:|---------:|:--------------------|:--------------------|:-----------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| line_number | int64          |       5537 |      0 |     5537 | 1                   | 5537                | 2769.0     | 1 (1); 2 (1); 3 (1) ... (5537 unique)                                                                                                                                                                                                                                    |
| user        | str            |       4283 |   1254 |        3 |                     |                     |            | jhall (2202); twhite (1172); ahayes (909)                                                                                                                                                                                                                                |
| client_ip   | str            |       4283 |   1254 |        4 |                     |                     |            | 192.168.230.165 (2170); 192.168.230.95 (1172); 192.168.231.127 (909); 192.168.230.122 (32)                                                                                                                                                                               |
| client_port | float64        |       4283 |   1254 |       67 | 33244.0             | 60795.0             | 52848.4707 | 59814.0 (1256); 59384.0 (723); 46011.0 (191) ... (67 unique)                                                                                                                                                                                                             |
| message     | str            |       5537 |      0 |     1599 |                     |                     |            | Outgoing Data Channel: Cipher 'AES-256-CBC' initialized with 256 bit key (235); Outgoing Data Channel: Using 160 bit message hash 'SHA1' for HMAC authentication (235); Incoming Data Channel: Cipher 'AES-256-CBC' initialized with 256 bit key (235) ... (1599 unique) |
| event_type  | str            |       5537 |      0 |        9 |                     |                     |            | peer_info (2181); other (1172); data_channel (940); tls_verify (676); tls (172)                                                                                                                                                                                          |
| timestamp   | datetime64[us] |       5537 |      0 |      375 | 2022-01-21 00:09:11 | 2022-01-24 23:12:27 |            | 2022-01-21 06:30:01 (26); 2022-01-21 08:49:04 (26); 2022-01-21 09:40:01 (26) ... (375 unique)                                                                                                                                                                            |


### OpenVPN -- Sample Data (first 5 rows)

```
   line_number        timestamp_raw   user        client_ip  client_port                                                      message  event_type  parse_error           timestamp
0            1  2022-01-21 00:09:11  jhall  192.168.230.165      46011.0      TLS: soft reset sec=3308/3308 bytes=45748/-1 pkts=649/0         tls        False 2022-01-21 00:09:11
1            2  2022-01-21 00:09:11  jhall  192.168.230.165      46011.0  VERIFY OK: depth=1, C=AT, ST=Vienna, L=Vienna, O=Some Or...  tls_verify        False 2022-01-21 00:09:11
2            3  2022-01-21 00:09:11  jhall  192.168.230.165      46011.0                                                 VERIFY KU OK  tls_verify        False 2022-01-21 00:09:11
3            4  2022-01-21 00:09:11  jhall  192.168.230.165      46011.0                    Validating certificate extended key usage       other        False 2022-01-21 00:09:11
4            5  2022-01-21 00:09:11  jhall  192.168.230.165      46011.0  ++ Certificate has EKU (str) TLS Web Client Authenticati...       other        False 2022-01-21 00:09:11
```


### Audit Log (internal_share) -- Field-Level Profile

**Rows:** 732 | **Columns:** 19

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-21 00:17:01.474999905+00:00 to 2022-01-24 23:17:01.967000008+00:00 (span: 3 days 23:00:00.492000103)

| Column       | Type                |   Non-Null |   Null |   Unique | Min                                 | Max                                 | Mean            | Top Values                                                                                                                                 |
|:-------------|:--------------------|-----------:|-------:|---------:|:------------------------------------|:------------------------------------|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------|
| line_number  | int64               |        732 |      0 |      732 | 1                                   | 732                                 | 366.5           | 1 (1); 2 (1); 3 (1) ... (732 unique)                                                                                                       |
| event_type   | str                 |        732 |      0 |       11 |                                     |                                     |                 | USER_ACCT (106); CRED_ACQ (106); LOGIN (106); USER_START (106); CRED_DISP (106)                                                            |
| audit_serial | int64               |        732 |      0 |      724 | 149                                 | 872                                 | 507.0           | 193 (3); 194 (3); 195 (3) ... (724 unique)                                                                                                 |
| pid          | float64             |        728 |      4 |      108 | 1.0                                 | 32269.0                             | 14583.9753      | 1.0 (84); 30310.0 (8); 1716.0 (6) ... (108 unique)                                                                                         |
| uid          | float64             |        724 |      8 |        1 | 0.0                                 | 0.0                                 | 0.0000          | 0.0 (724)                                                                                                                                  |
| auid         | float64             |        724 |      8 |        2 | 0.0                                 | 4294967295.0                        | 1779682580.8011 | 0.0 (424); 4294967295.0 (300)                                                                                                              |
| ses          | str                 |        724 |      8 |      107 |                                     |                                     |                 | 4294967295 (300); 36 (4); 37 (4) ... (107 unique)                                                                                          |
| acct         | str                 |        530 |    202 |        1 |                                     |                                     |                 | root (530)                                                                                                                                 |
| exe          | str                 |        618 |    114 |        3 |                                     |                                     |                 | /usr/sbin/cron (530); /lib/systemd/systemd (84); /sbin/apparmor_parser (4)                                                                 |
| op           | str                 |        530 |    202 |        4 |                                     |                                     |                 | PAM:setcred (212); PAM:accounting (106); PAM:session_open (106); PAM:session_close (106)                                                   |
| result       | str                 |        720 |     12 |        2 |                                     |                                     |                 | success (614); 1 (106)                                                                                                                     |
| terminal     | str                 |        614 |    118 |        2 |                                     |                                     |                 | cron (530); ? (84)                                                                                                                         |
| hostname     | str                 |        614 |    118 |        1 |                                     |                                     |                 | ? (614)                                                                                                                                    |
| addr         | str                 |        614 |    118 |        1 |                                     |                                     |                 | ? (614)                                                                                                                                    |
| unit         | object              |          0 |    732 |        0 |                                     |                                     |                 |                                                                                                                                            |
| comm         | str                 |          8 |    724 |        1 |                                     |                                     |                 | apparmor_parser (8)                                                                                                                        |
| timestamp    | datetime64[ns, UTC] |        732 |      0 |      360 | 2022-01-21 00:17:01.474999905+00:00 | 2022-01-24 23:17:01.967000008+00:00 |                 | 2022-01-21 06:17:32.062999964+00:00 (6); 2022-01-23 14:17:01.190000057+00:00 (6); 2022-01-21 07:07:01.878999949+00:00 (4) ... (360 unique) |


### Audit Log (internal_share) -- Sample Data (first 5 rows)

```
   line_number  event_type  timestamp_epoch  audit_serial     pid  uid          auid         ses  acct             exe                op   result terminal hostname addr  unit comm  parse_error                           timestamp
0            1   USER_ACCT     1.642724e+09           149  1716.0  0.0  4.294967e+09  4294967295  root  /usr/sbin/cron    PAM:accounting  success     cron        ?    ?  None  NaN        False 2022-01-21 00:17:01.474999905+00:00
1            2    CRED_ACQ     1.642724e+09           150  1716.0  0.0  4.294967e+09  4294967295  root  /usr/sbin/cron       PAM:setcred  success     cron        ?    ?  None  NaN        False 2022-01-21 00:17:01.479000092+00:00
2            3       LOGIN     1.642724e+09           151  1716.0  0.0  0.000000e+00          36   NaN             NaN               NaN        1      NaN      NaN  NaN  None  NaN        False 2022-01-21 00:17:01.479000092+00:00
3            4  USER_START     1.642724e+09           152  1716.0  0.0  0.000000e+00          36  root  /usr/sbin/cron  PAM:session_open  success     cron        ?    ?  None  NaN        False 2022-01-21 00:17:01.483000040+00:00
4            5   CRED_DISP     1.642724e+09           153  1716.0  0.0  0.000000e+00          36  root  /usr/sbin/cron       PAM:setcred  success     cron        ?    ?  None  NaN        False 2022-01-21 00:17:01.490999937+00:00
```


### CPU Monitoring -- Field-Level Profile

**Rows:** 1,920 | **Columns:** 12

**Parse Errors:** 0 (0.0%)

**Time Range:** 2022-01-24 00:00:22.284000+00:00 to 2022-01-24 23:59:37.284000+00:00 (span: 0 days 23:59:15)

| Column         | Type                |   Non-Null |   Null |   Unique | Min                              | Max                              | Mean   | Top Values                                                                                                                         |
|:---------------|:--------------------|-----------:|-------:|---------:|:---------------------------------|:---------------------------------|:-------|:-----------------------------------------------------------------------------------------------------------------------------------|
| line_number    | int64               |       1920 |      0 |     1920 | 1                                | 1920                             | 960.5  | 1 (1); 2 (1); 3 (1) ... (1920 unique)                                                                                              |
| hostname       | str                 |       1920 |      0 |        1 |                                  |                                  |        | intranet-server (1920)                                                                                                             |
| cpu_total_pct  | float64             |       1920 |      0 |      276 | 0.0363                           | 1.0                              | 0.0894 | 1.0 (46); 0.0651 (39); 0.0648 (32) ... (276 unique)                                                                                |
| cpu_user_pct   | float64             |       1920 |      0 |      182 | 0.0162                           | 0.1562                           | 0.0287 | 0.0278 (71); 0.028 (66); 0.0273 (65) ... (182 unique)                                                                              |
| cpu_system_pct | float64             |       1920 |      0 |      216 | 0.0145                           | 0.0799                           | 0.0347 | 0.0351 (52); 0.0353 (48); 0.0362 (46) ... (216 unique)                                                                             |
| cpu_idle_pct   | float64             |       1920 |      0 |      292 | 0.0                              | 0.9631                           | 0.9095 | 0.0 (48); 0.9349 (34); 0.935 (32) ... (292 unique)                                                                                 |
| cpu_iowait_pct | float64             |       1920 |      0 |       66 | 0.0                              | 0.1134                           | 0.0011 | 0.0002 (497); 0.0005 (360); 0.0 (284) ... (66 unique)                                                                              |
| cpu_steal_pct  | float64             |       1920 |      0 |        4 | 0.0                              | 0.0007                           | 0.0006 | 0.0005 (945); 0.0007 (925); 0.0 (48); 0.0002 (2)                                                                                   |
| cores          | int64               |       1920 |      0 |        1 | 1                                | 1                                | 1.0    | 1 (1920)                                                                                                                           |
| timestamp      | datetime64[us, UTC] |       1920 |      0 |     1920 | 2022-01-24 00:00:22.284000+00:00 | 2022-01-24 23:59:37.284000+00:00 |        | 2022-01-24 00:00:22.284000+00:00 (1); 2022-01-24 00:01:07.284000+00:00 (1); 2022-01-24 00:01:52.284000+00:00 (1) ... (1920 unique) |


### CPU Monitoring -- Sample Data (first 5 rows)

```
   line_number             timestamp_raw         hostname  cpu_total_pct  cpu_user_pct  cpu_system_pct  cpu_idle_pct  cpu_iowait_pct  cpu_steal_pct  cores  parse_error                        timestamp
0            1  2022-01-24T00:00:22.284Z  intranet-server         0.0640        0.0273          0.0360        0.9358          0.0002         0.0005      1        False 2022-01-24 00:00:22.284000+00:00
1            2  2022-01-24T00:01:07.284Z  intranet-server         0.0633        0.0278          0.0346        0.9339          0.0028         0.0007      1        False 2022-01-24 00:01:07.284000+00:00
2            3  2022-01-24T00:01:52.284Z  intranet-server         0.0643        0.0294          0.0344        0.9355          0.0002         0.0005      1        False 2022-01-24 00:01:52.284000+00:00
3            4  2022-01-24T00:02:37.284Z  intranet-server         0.0645        0.0286          0.0347        0.9350          0.0005         0.0007      1        False 2022-01-24 00:02:37.284000+00:00
4            5  2022-01-24T00:03:22.284Z  intranet-server         0.0637        0.0292          0.0328        0.9361          0.0002         0.0005      1        False 2022-01-24 00:03:22.284000+00:00
```


## 4. Label Analysis


### 4.1 Label Coverage Per Log File

| Log                        | Host            | Total Lines   | Labeled   | Unlabeled   | % Labeled   |
|:---------------------------|:----------------|:--------------|:----------|:------------|:------------|
| DNS (dnsmasq)              | inet-firewall   | 275,900       | 54,035    | 221,865     | 19.6%       |
| Apache Access (intranet)   | intranet_server | 8,530         | 7,695     | 835         | 90.2%       |
| Apache Error (intranet)    | intranet_server | 36            | 36        | 0           | 100.0%      |
| Audit Log (intranet)       | intranet_server | 2,316         | 9         | 2,307       | 0.4%        |
| Auth Log (intranet)        | intranet_server | 272           | 8         | 264         | 2.9%        |
| OpenVPN                    | vpn             | 5,537         | 28        | 5,509       | 0.5%        |
| Audit Log (internal_share) | internal_share  | 732           | 2         | 730         | 0.3%        |
| CPU Monitoring             | monitoring      | 1,920         | 49        | 1,871       | 2.6%        |


### 4.2 Label Frequency Distribution

| Label                  | Count   | Phase        |
|:-----------------------|:--------|:-------------|
| dnsteal                | 53,056  | exfiltration |
| attacker               | 53,056  | unknown      |
| dnsteal-received       | 53,006  | exfiltration |
| foothold               | 8,724   | foothold     |
| attacker_http          | 7,723   | foothold     |
| dirb                   | 4,493   | foothold     |
| wpscan                 | 3,207   | foothold     |
| service_scan           | 455     | foothold     |
| dns_scan               | 414     | foothold     |
| network_scan           | 92      | foothold     |
| escalate               | 82      | escalate     |
| crack_passwords        | 49      | foothold     |
| dnsteal-dropped        | 48      | exfiltration |
| webshell_cmd           | 44      | foothold     |
| attacker_vpn           | 28      | foothold     |
| escalated_command      | 10      | escalate     |
| escalated_sudo_command | 10      | escalate     |
| attacker_change_user   | 8       | escalate     |
| traceroute             | 4       | foothold     |
| webshell_upload        | 3       | foothold     |
| escalated_sudo_session | 3       | escalate     |
| exfiltration-service   | 2       | exfiltration |


### 4.3 Labels by Attack Phase

| Phase        | Labeled Lines   |
|:-------------|:----------------|
| exfiltration | 53,056          |
| foothold     | 8,789           |
| escalate     | 17              |


### 4.4 Label Co-occurrence (Top 15 Combinations)

| Label Combination                   | Count   |
|:------------------------------------|:--------|
| attacker|dnsteal|dnsteal-received   | 53,006  |
| attacker_http|dirb|foothold         | 4,485   |
| attacker_http|foothold|wpscan       | 3,199   |
| foothold|service_scan               | 447     |
| dns_scan|foothold                   | 414     |
| foothold|network_scan               | 92      |
| crack_passwords|escalate            | 49      |
| attacker|dnsteal|dnsteal-dropped    | 48      |
| attacker_http|foothold|webshell_cmd | 28      |
| attacker_vpn|foothold               | 28      |
| escalate|webshell_cmd               | 16      |
| dirb|foothold                       | 8       |
| foothold|wpscan                     | 8       |
| attacker_http|foothold|service_scan | 8       |
| attacker_change_user|escalate       | 7       |


### 4.5 Labels by Source Log

| Log                        | Phase        | Count   |
|:---------------------------|:-------------|:--------|
| Apache Access (intranet)   | foothold     | 7,695   |
| Apache Error (intranet)    | foothold     | 36      |
| Audit Log (internal_share) | exfiltration | 2       |
| Audit Log (intranet)       | escalate     | 9       |
| Auth Log (intranet)        | escalate     | 8       |
| CPU Monitoring             | foothold     | 49      |
| DNS (dnsmasq)              | exfiltration | 53,054  |
| DNS (dnsmasq)              | foothold     | 981     |
| OpenVPN                    | foothold     | 28      |


### 4.6 Scenario Impact on Labels

Which labels would survive under each scenario:


| Scenario               | Labeled Lines   |   Log Sources with Labels |
|:-----------------------|:----------------|--------------------------:|
| scenario (full)        | 61,862          |                         8 |
| scenario1 (no exfil)   | 7,827           |                         7 |
| scenario2 (exfil only) | 54,046          |                         3 |


## 5. Attacker Timeline

**Total attack actions:** 55

**Attack window:** 2022-01-24 03:01:00.063877+00:00 to 2022-01-24 13:50:03.250776+00:00 (duration: 0 days 10:49:03.186899)


### Full Attack Timeline

```
                       timestamp                action
2022-01-24 03:01:00.063877+00:00           vpn_connect
2022-01-24 03:01:17.723042+00:00   traceroute_internet
2022-01-24 03:01:20.969099+00:00       dns_brute_force
2022-01-24 03:01:28.456313+00:00     host_discover_dmz
2022-01-24 03:36:38.963403+00:00   host_discover_local
2022-01-24 03:56:46.825579+00:00          service_scan
2022-01-24 03:57:26.435577+00:00 recon_networks_finish
2022-01-24 03:57:26.436714+00:00             dirb_scan
2022-01-24 03:57:48.934650+00:00                wpscan
2022-01-24 03:58:20.020490+00:00      upload_rce_shell
2022-01-24 03:58:23.348462+00:00          check_whoami
2022-01-24 03:58:25.108981+00:00         check_uname_r
2022-01-24 03:58:27.041422+00:00          read_profile
2022-01-24 03:58:28.528493+00:00             check_who
2022-01-24 03:58:30.292820+00:00         check_meminfo
2022-01-24 03:58:33.828771+00:00         check_uname_a
2022-01-24 03:58:36.383526+00:00         check_user_id
2022-01-24 03:58:39.247353+00:00              check_df
2022-01-24 03:58:40.944504+00:00     check_netstat_nat
2022-01-24 03:58:42.198977+00:00              check_id
2022-01-24 03:58:43.400876+00:00           read_resolv
2022-01-24 03:58:44.632721+00:00       check_netstat_t
2022-01-24 03:58:48.259736+00:00             list_home
2022-01-24 03:58:49.562813+00:00            check_last
2022-01-24 03:58:51.585727+00:00          list_web_dir
2022-01-24 03:58:54.219952+00:00            check_date
2022-01-24 03:58:55.463292+00:00              list_www
2022-01-24 03:58:57.641124+00:00       check_netstat_l
2022-01-24 03:59:00.791636+00:00                 clear
2022-01-24 03:59:02.283150+00:00       check_wp_config
2022-01-24 03:59:03.740619+00:00            check_ps_a
2022-01-24 03:59:05.928341+00:00           read_passwd
2022-01-24 03:59:09.511060+00:00         check_release
2022-01-24 03:59:12.977191+00:00         check_cpuinfo
2022-01-24 03:59:14.207842+00:00         dump_wp_users
2022-01-24 03:59:16.923431+00:00            read_group
2022-01-24 03:59:18.310719+00:00          check_uptime
2022-01-24 03:59:19.790753+00:00  check_network_config
2022-01-24 03:59:22.176229+00:00     recon_host_finish
2022-01-24 03:59:22.177425+00:00   decide_crack_method
2022-01-24 03:59:22.182453+00:00          crack_wphash
2022-01-24 04:36:57.885350+00:00  reverse_shell_listen
2022-01-24 04:36:59.577594+00:00    open_reverse_shell
2022-01-24 04:37:25.836115+00:00    wait_reverse_shell
2022-01-24 04:37:39.739109+00:00              open_pty
2022-01-24 04:37:40.530254+00:00            login_user
2022-01-24 04:37:53.496765+00:00            read_fstab
2022-01-24 04:37:55.374578+00:00          check_ps_aux
2022-01-24 04:37:58.370156+00:00            check_sudo
2022-01-24 04:38:01.850376+00:00        check_uname_ar
2022-01-24 04:38:04.866547+00:00           list_shadow
2022-01-24 04:38:06.227784+00:00           read_shadow
2022-01-24 04:38:09.938128+00:00        check_ifconfig
2022-01-24 04:38:11.767134+00:00        vpn_disconnect
2022-01-24 13:50:03.250776+00:00          dnsteal_stop
```

**Foothold phase:** 2022-01-24T03:01:00.064Z to 2022-01-24T03:59:22.182Z

**Password cracking:** 2022-01-24T03:59:22.182Z to 2022-01-24T04:36:57.884Z

**Escalation phase:** 2022-01-24T04:36:57.885Z to 2022-01-24T04:38:13.932Z

**Escalated to user:** jhall


## 6. Employee Behavior Analysis

| Employee            | Events   | Time Range                                                                 |   Unique States |   Unique Transitions | Top States                                                                    |
|:--------------------|:---------|:---------------------------------------------------------------------------|----------------:|---------------------:|:------------------------------------------------------------------------------|
| internal_employee_0 | 999      | 2022-01-20 13:46:57.247622728+00:00 to 2022-01-20 22:00:17.501622676+00:00 |              41 |                   76 | horde_mails_page(107); selecting_activity(88); owncloud_all_files(84)         |
| internal_employee_1 | 9,606    | 2022-01-20 13:46:45.939522505+00:00 to 2022-01-24 21:32:49.165823221+00:00 |              33 |                   64 | horde_mails_page(1445); horde_mail_compose(1146); selecting_activity(802)     |
| internal_employee_2 | 8,716    | 2022-01-20 13:46:57.423593760+00:00 to 2022-01-24 18:42:31.524244069+00:00 |              42 |                   87 | horde_mails_page(1148); selecting_activity(622); horde_selecting_menu(557)    |
| internal_employee_3 | 9,063    | 2022-01-20 13:46:45.446353912+00:00 to 2022-01-24 22:00:09.718875647+00:00 |              42 |                   87 | horde_mails_page(1101); selecting_activity(770); horde_mail_compose(551)      |
| remote_employee_0   | 12,797   | 2022-01-20 13:46:45.480020046+00:00 to 2022-01-24 21:58:18.561034441+00:00 |              37 |                   66 | selecting_activity(2596); horde_mails_page(1065); horde_selecting_menu(809)   |
| remote_employee_1   | 9,723    | 2022-01-20 13:46:46.365256786+00:00 to 2022-01-24 17:45:35.852435112+00:00 |              36 |                   67 | selecting_activity(2094); horde_mails_page(852); horde_selecting_menu(518)    |
| remote_employee_2   | 1,873    | 2022-01-20 13:46:45.312391758+00:00 to 2022-01-23 16:31:55.566637754+00:00 |              33 |                   55 | selecting_activity(213); wpdiscuz_comment_compose(95); wpdiscuz_post_page(85) |
| ext_user_0          | 6,140    | 2022-01-20 13:46:58.470061064+00:00 to 2022-01-24 19:22:55.706752777+00:00 |               9 |                   17 | horde_mails_page(2267); horde_mail_compose(1260); horde_mail_view(806)        |
| ext_user_1          | 4,376    | 2022-01-20 13:46:57.314561844+00:00 to 2022-01-24 18:03:46.524682283+00:00 |               9 |                   17 | horde_mails_page(1435); horde_mail_compose(920); horde_mail_view(600)         |
| ext_user_2          | 5,045    | 2022-01-20 13:46:59.823548317+00:00 to 2022-01-24 19:23:45.880274773+00:00 |               9 |                   17 | horde_mails_page(1594); horde_mail_compose(1055); horde_mail_view(688)        |


## 7. Cross-Log Correlation Analysis


### 7.1 IP Address Overlap

**Attacker IPs** (`172.19.131.174` VPN-internal, `192.168.230.122` external) **found in:**

  - DNS (dnsmasq) (via 172.19.131.174)

  - Apache Access (intranet) (via 172.19.131.174)

  - Apache Error (intranet) (via 172.19.131.174)

  - OpenVPN (via 192.168.230.122)


### 7.2 Shared IPs Between Log Types

| Log 1                    | Log 2                    |   Shared IPs | Examples                                                          |
|:-------------------------|:-------------------------|-------------:|:------------------------------------------------------------------|
| DNS (dnsmasq)            | Apache Access (intranet) |            5 | 10.143.2.25, 10.143.2.4, 10.143.2.91, 10.143.3.65, 172.19.131.174 |
| DNS (dnsmasq)            | Apache Error (intranet)  |            1 | 172.19.131.174                                                    |
| Apache Access (intranet) | Apache Error (intranet)  |            1 | 172.19.131.174                                                    |


### 7.3 Attacker Trace Across Logs

Tracking attacker IPs (`172.19.131.174` (VPN-internal), `192.168.230.122` (external)) across all log sources:


**DNS (dnsmasq):** 11,065 events from attacker (IPs: 172.19.131.174), time range: 2022-01-21 00:11:18 to 2022-01-24 22:42:21

**Apache Access (intranet):** 8,027 events from attacker (IPs: 172.19.131.174), time range: 2022-01-23 07:54:24+00:00 to 2022-01-24 04:37:25+00:00

**Apache Error (intranet):** 36 events from attacker (IPs: 172.19.131.174), time range: 2022-01-24 03:57:26.696483 to 2022-01-24 03:58:09.826189

**OpenVPN:** 32 events from attacker (IPs: 192.168.230.122), time range: 2022-01-24 03:01:00 to 2022-01-24 04:42:05


## 8. Data Quality Assessment

| Log                        | Total Rows   | Parse Errors   | Timestamp Nulls   |
|:---------------------------|:-------------|:---------------|:------------------|
| DNS (dnsmasq)              | 275,900      | 0 (0.0%)       | 0 (0.0%)          |
| Apache Access (intranet)   | 8,530        | 0 (0.0%)       | 0 (0.0%)          |
| Apache Error (intranet)    | 36           | 0 (0.0%)       | 0 (0.0%)          |
| Audit Log (intranet)       | 2,316        | 0 (0.0%)       | 0 (0.0%)          |
| Auth Log (intranet)        | 272          | 0 (0.0%)       | 0 (0.0%)          |
| OpenVPN                    | 5,537        | 0 (0.0%)       | 0 (0.0%)          |
| Audit Log (internal_share) | 732          | 0 (0.0%)       | 0 (0.0%)          |
| CPU Monitoring             | 1,920        | 0 (0.0%)       | 0 (0.0%)          |


## 9. Schema Readiness Assessment


### 9.1 Proposed Table Mapping

| Table          | Source               | Rows    | PK           | Key Columns                                            |
|:---------------|:---------------------|:--------|:-------------|:-------------------------------------------------------|
| hosts          | servers.yaml         | 22      | host_id      | hostname, ip, zone, os                                 |
| log_events     | All 8 log files      | 295,243 | event_id     | host_id(FK), timestamp, log_type, line_number          |
| attack_labels  | All 8 label files    | 61,862  | label_id     | event_id(FK), label_name, phase, rule_name             |
| http_events    | Apache access+error  | 8,566   | event_id(FK) | client_ip, method, path, status_code, user_agent       |
| dns_events     | dnsmasq.log          | 275,900 | event_id(FK) | domain, query_type, action, client_ip, is_exfiltration |
| auth_events    | auth.log + audit.log | 3,320   | event_id(FK) | event_type, username, service, result                  |
| vpn_events     | openvpn.log          | 5,537   | event_id(FK) | user, client_ip, event_type                            |
| system_metrics | cpu.log              | 1,920   | event_id(FK) | cpu_total_pct, cpu_user_pct, cpu_system_pct            |


### 9.2 SQL Type Mapping (Auto-Detected)

Mapping derived from actual parsed column types:


| Column          | Python Type    | SQL Type                     | Source                   |
|:----------------|:---------------|:-----------------------------|:-------------------------|
| action          | str            | VARCHAR(20)                  | DNS (dnsmasq)            |
| query_type      | str            | VARCHAR(20)                  | DNS (dnsmasq)            |
| domain          | str            | VARCHAR(309)                 | DNS (dnsmasq)            |
| client_ip       | str            | VARCHAR(45)                  | DNS (dnsmasq)            |
| extra_ip        | str            | VARCHAR(45)                  | DNS (dnsmasq)            |
| is_exfiltration | bool           | BOOLEAN                      | DNS (dnsmasq)            |
| timestamp       | datetime64[us] | TIMESTAMP WITH TIME ZONE     | DNS (dnsmasq)            |
| method          | str            | VARCHAR(20)                  | Apache Access (intranet) |
| path            | str            | VARCHAR(145)                 | Apache Access (intranet) |
| query_string    | str            | VARCHAR(294)                 | Apache Access (intranet) |
| protocol        | str            | VARCHAR(20)                  | Apache Access (intranet) |
| status_code     | int64          | INTEGER                      | Apache Access (intranet) |
| bytes_sent      | int64          | INTEGER                      | Apache Access (intranet) |
| referer         | str            | VARCHAR(201)                 | Apache Access (intranet) |
| user_agent      | str            | VARCHAR(168)                 | Apache Access (intranet) |
| module          | str            | VARCHAR(20)                  | Apache Error (intranet)  |
| level           | str            | VARCHAR(20)                  | Apache Error (intranet)  |
| pid             | int64          | INTEGER                      | Apache Error (intranet)  |
| client          | str            | VARCHAR(30)                  | Apache Error (intranet)  |
| message         | str            | TEXT (max observed len: 331) | Apache Error (intranet)  |
| event_type      | str            | VARCHAR(20)                  | Audit Log (intranet)     |
| audit_serial    | int64          | INTEGER                      | Audit Log (intranet)     |
| uid             | float64        | DECIMAL(10,4)                | Audit Log (intranet)     |
| auid            | float64        | DECIMAL(10,4)                | Audit Log (intranet)     |
| ses             | str            | VARCHAR(20)                  | Audit Log (intranet)     |
| acct            | str            | VARCHAR(20)                  | Audit Log (intranet)     |
| exe             | str            | VARCHAR(31)                  | Audit Log (intranet)     |
| op              | str            | VARCHAR(27)                  | Audit Log (intranet)     |
| result          | str            | VARCHAR(20)                  | Audit Log (intranet)     |
| terminal        | str            | VARCHAR(20)                  | Audit Log (intranet)     |
| hostname        | str            | VARCHAR(21)                  | Audit Log (intranet)     |
| addr            | str            | VARCHAR(21)                  | Audit Log (intranet)     |
| unit            | object         | TEXT                         | Audit Log (intranet)     |
| comm            | str            | VARCHAR(22)                  | Audit Log (intranet)     |
| service         | str            | VARCHAR(21)                  | Auth Log (intranet)      |
| username        | str            | VARCHAR(20)                  | Auth Log (intranet)      |
| user            | str            | VARCHAR(20)                  | OpenVPN                  |
| client_port     | float64        | DECIMAL(10,4)                | OpenVPN                  |
| cpu_total_pct   | float64        | DECIMAL(10,4)                | CPU Monitoring           |
| cpu_user_pct    | float64        | DECIMAL(10,4)                | CPU Monitoring           |
| cpu_system_pct  | float64        | DECIMAL(10,4)                | CPU Monitoring           |
| cpu_idle_pct    | float64        | DECIMAL(10,4)                | CPU Monitoring           |
| cpu_iowait_pct  | float64        | DECIMAL(10,4)                | CPU Monitoring           |
| cpu_steal_pct   | float64        | DECIMAL(10,4)                | CPU Monitoring           |
| cores           | int64          | INTEGER                      | CPU Monitoring           |


### 9.3 Actual Row Counts (From Parsing)

| Log                        | Parsed Rows   | Label Rows   |
|:---------------------------|:--------------|:-------------|
| DNS (dnsmasq)              | 275,900       | 54,035       |
| Apache Access (intranet)   | 8,530         | 7,695        |
| Apache Error (intranet)    | 36            | 36           |
| Audit Log (intranet)       | 2,316         | 9            |
| Auth Log (intranet)        | 272           | 8            |
| OpenVPN                    | 5,537         | 28           |
| Audit Log (internal_share) | 732           | 2            |
| CPU Monitoring             | 1,920         | 49           |
| **TOTAL**                  | **295,243**   |              |


### 9.4 Project Requirement Check

| Requirement            | Threshold   | Actual                                                           | Status   |
|:-----------------------|:------------|:-----------------------------------------------------------------|:---------|
| 50,000+ total rows     | 50,000      | 295,243                                                          | PASS     |
| 10+ attributes         | 10          | 46                                                               | PASS     |
| 4+ relational tables   | 4           | 8                                                                | PASS     |
| Time attributes        | Required    | timestamp                                                        | PASS     |
| Categorical attributes | Required    | None found                                                       | FAIL     |
| Numeric attributes     | Required    | audit_serial, auid, bytes_sent, client_port, cores, cpu_idle_pct | PASS     |
| Requires normalization | Required    | Yes -- 7 different log formats                                   | PASS     |


## 10. Recommendations

**Dataset Selection:** The full "scenario" includes all 3 attack phases (escalate, exfiltration, foothold) with 22 distinct label types across 61,862 labeled lines (21.0% of 295,243 total rows). This is the richest scenario available.

**Schema Design:** Based on 7 distinct log formats parsed, we propose 8 tables. The design is scenario-agnostic; label data naturally handles different scenarios via the attack_labels table.

**Key Risk:** The largest log source ("DNS (dnsmasq)") accounts for 275,900 rows (93.4% of total). The smallest ("Apache Error (intranet)") has only 36 rows. Consider partitioning or sampling the dominant log type for dashboards.

**Normalization:** Required -- 7 completely different log formats yield 46 unique attributes. Unifying into a star schema (log_events fact + type-specific dimensions) achieves 3NF.

**Advanced Query Ideas** (derived from cross-log analysis):

  - DNS exfiltration detection: window function on the 275,900 DNS rows to compute query frequency per minute

  - Reconstruct attack timeline: CTE + UNION across all 8 log types, joined with attack_labels

  - CPU anomaly detection: analyze 1,920 metric samples for spikes correlated with attack phases

  - Simulate alternative scenarios: filter labels by rule source to show scenario1 vs scenario2 impact

  - Cross-host attacker trace: join log_events + hosts on IP (attacker appears in 4 log sources)


---
*Report generated in 83.2 seconds.*