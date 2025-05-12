    def __select_identifiers(self, models: dict):
        """
        Haalt alle identifiers op uit het model ten behoeve van de aanmaken van BKeys in de entiteiten en DDL's

        Args:
            models (dict): de JSON (RETW Output) geconverteerd naar een dictionary
        Returns:
            identifiers (dict): een dictionary met daarin alle informatie van de identifier benodigd voor het aanmaken van BKeys
        """
        def _build_identifier_strings(identifier, mapping, attributemapping, attribute_target):
            if "AttributesSource" in attributemapping:
                if identifier["IsPrimary"]:
                    identifier_string_entity = f"[{identifier['EntityCode']}BKey] nvarchar(200) NOT NULL"
                    identifier_string = f"[{identifier['EntityCode']}BKey] =  '{mapping['DataSource']}' + '-' + CAST({attributemapping['AttributesSource']['IdEntity']}.[{attributemapping['AttributesSource']['Code']}] AS NVARCHAR(50))"
                else:
                    identifier_string_entity = f"[{identifier['Code']}BKey] nvarchar(200) NOT NULL"
                    identifier_string = f"{attribute_target}BKey =  '{mapping['DataSource']}' + '-' + CAST({attributemapping['AttributesSource']['IdEntity']}.[{attributemapping['AttributesSource']['Code']}] AS NVARCHAR(50))"
            else:
                if identifier["IsPrimary"]:
                    identifier_string_entity = f"[{identifier['EntityCode']}BKey] nvarchar(200) NOT NULL"
                    identifier_string = f"[{identifier['EntityCode']}BKey] = '{mapping['DataSource']}' +  '-' +  {attributemapping['Expression']}"
                else:
                    identifier_string_entity = f"[{identifier['Code']}BKey] nvarchar(200) NOT NULL"
                    identifier_string = f"[{attribute_target}BKey] = '{mapping['DataSource']}' +  '-' +  {attributemapping['Expression']}"
            return {
                "IdentifierId": identifier["Id"],
                "IdentifierStringEntity": identifier_string_entity,
                "IdentifierStringSourceview": identifier_string,
            }

        def _process_mapping(mapping, identifiers, strings):
            if "Identifiers" not in mapping["EntityTarget"]:
                logger.error(f"Geen identifiers aanwezig voor entitytarget {mapping['EntityTarget']['Name']}")
                return
            for identifier in mapping["EntityTarget"]["Identifiers"]:
                id_entity_identifier = identifier["EntityID"]
                if "AttributeMapping" not in mapping:
                    logger.error(f"Geen attribute mapping aanwezig voor entity {mapping['EntityTarget']['Name']}")
                    continue
                for attributemapping in mapping["AttributeMapping"]:
                    id_attribute_target = attributemapping["AttributeTarget"]["IdEntity"]
                    attribute_target = attributemapping["AttributeTarget"]["Code"]
                    if id_attribute_target == id_entity_identifier:
                        strings[identifier["Id"]] = _build_identifier_strings(
                            identifier, mapping, attributemapping, attribute_target
                        )
                identifier_string_entity = strings[identifier["Id"]]["IdentifierStringEntity"] if identifier["Id"] in strings else ""
                identifier_string = strings[identifier["Id"]]["IdentifierStringSourceview"] if identifier["Id"] in strings else ""
                identifiers[identifier["Id"]] = {
                    "IdentifierID": identifier["Id"],
                    "IdentifierName": identifier["Name"],
                    "IdentifierCode": identifier["Code"],
                    "EntityId": identifier["EntityID"],
                    "EntityCode": identifier["EntityCode"],
                    "IsPrimary": identifier["IsPrimary"],
                    "IdentifierStringEntity": identifier_string_entity,
                    "IdentifierStringSourceView": identifier_string,
                }

        identifiers = {}
        if "Mappings" in models:
            strings = {}
            for mapping in models["Mappings"]:
                _process_mapping(mapping, identifiers, strings)
        return identifiers