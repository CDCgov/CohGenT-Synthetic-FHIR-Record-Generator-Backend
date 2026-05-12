

def get_condition_list():
    conditions = {
        "conditionList": [
            {
                "name": "COVID-19",
                "primaryCodes": [
                    {
                        "display": "COVID-19",
                        "code": "840539006",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Acute COVID-19",
                        "code": "119302008",
                        "system": "http://snomed.info/sct"
                    },
                ],
                "secondaryCodes": [
                    {
                        "display": "Acute respiratory distress syndrome due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "674814021000119000",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Lymphocytopenia due to severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "866151004",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Thrombocytopenia due to severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "866152006",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Sepsis due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "870588003",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Acute kidney injury due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "870589006",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Acute hypoxemic respiratory failure due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "870590002",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Rhabdomyolysis due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "870591003",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Infection of lower respiratory tract caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
                        "code": "880529761000119000",
                        "system": "http://snomed.info/sct"
                    }
                ]
            },
            {
                "name": "Tuberculosis",
                "primaryCodes": [
                    {
                        "display": "Tuberculosis",
                        "code": "56717001",
                        "system": "http://snomed.info/sct"
                    }
                ]
            },
            {
                "name": "RSV",
                "primaryCodes": [
                    {
                        "display": "Respiratory syncytial virus bronchiolitis (disorder)",
                        "code": "57089007",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Respiratory syncytial virus infection (disorder)",
                        "code": "55735004",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Respiratory syncytial virus laryngotracheobronchitis (disorder)",
                        "code": "72204002",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Respiratory syncytial virus bronchitis (disorder)",
                        "code": "79479005",
                        "system": "http://snomed.info/sct"
                    }
                ],
                "secondaryCodes": [
                    {
                        "display": "Bronchopneumonia caused by respiratory syncytial virus (disorder)",
                        "code": "10625551000119100",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Acute respiratory syncytial virus bronchitis (disorder)",
                        "code": "195727009",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Acute bronchiolitis caused by respiratory syncytial virus (disorder)",
                        "code": "195739001",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Pneumonia caused by respiratory syncytial virus (disorder)",
                        "code": "195881003",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Respiratory syncytial virus pharyngitis (disorder)",
                        "code": "31309002",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Healthcare associated respiratory syncytial virus disease (disorder)",
                        "code": "408684006",
                        "system": "http://snomed.info/sct"
                    }
                ]
            },
            {
                "name": "Influenza",
                "primaryCodes": [
                    {
                        "display": "Influenza (disorder)",
                        "code": "6142004",
                        "system": "http://snomed.info/sct"
                    },
                ],
                "secondaryCodes": [
                    {
                        "display": "Influenza with pharyngitis (disorder)",
                        "code": "195924009",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Influenza with laryngitis (disorder)",
                        "code": "195923003",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Influenzal acute upper respiratory infection (disorder)",
                        "code": "43692000",
                        "system": "http://snomed.info/sct"
                    }
                ]
            },
            {
                "name": "Syphilis",
                "primaryCodes": [
                    {
                        "display": "Syphilis (disorder)",
                        "code": "76272004",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Primary syphilis (disorder)",
                        "code": "266127002",
                        "system": "http://snomed.info/sct"
                    },
                    {
                        "display": "Early symptomatic syphilis (disorder)",
                        "code": "186846005",
                        "system": "http://snomed.info/sct"
                    }
                ]
            }
        ]
    }
    return conditions