    def __copy_mdde_scripts(self):
        """
        Kopieer de MDDE scripts naar een Visual Studio Project repository folder
        """
        logger.info("Start copy of MDDE scripts to vs Project repo folder.")
        dir_output = (
            str(self.params["ProjectFolder"]) + "\\" + "CentralLayer" + "\\" + "DA_MDDE"
        )

        def _copy_file_and_update_dicts(schema, types, file, dir_output):
            # Add used folders to dict_created_ddls to be later used to add to the VS Project file
            if (
                schema.name
                not in self.dict_created_ddls["Folder Include"]
            ):
                self.dict_created_ddls["Folder Include"].append(
                    schema.name
                )
            if (
                schema.name + "\\" + types.name
                not in self.dict_created_ddls["Folder Include"]
            ):
                self.dict_created_ddls["Folder Include"].append(
                    schema.name + "\\" + types.name
                )
            if (
                schema.name + "\\" + types.name + "\\" + file.name
                not in self.dict_created_ddls["Build Include"]
            ):
                self.dict_created_ddls["Build Include"].append(
                    schema.name + "\\" + types.name + "\\" + file.name
                )
            dir_output_type = dir_output + "/" + types.name + "/"
            Path(dir_output_type).mkdir(parents=True, exist_ok=True)
            dest = Path(dir_output_type + file.name)
            logger.info(f"Copy {file} to: {dest.resolve()}")
            dest.write_text(file.read_text())

        def _process_types(schema, types, dir_output):
            if types.is_dir():
                logger.info(
                    f"Found folder: {self.params['MDDEFolder']}\{schema.parent.name}\{schema.name}\{types.name}."
                )
            for file in types.iterdir():
                if file.is_file():
                    _copy_file_and_update_dicts(schema, types, file, dir_output)

        def _process_schema(platform, schema, dir_output):
            if schema.is_dir():
                logger.info(
                    f"Found folder: {self.params['MDDEFolder']}\{platform.name}\{schema.name}."
                )
                for types in schema.iterdir():
                    _process_types(schema, types, dir_output)

        for platform in self.params["MDDEFolder"].iterdir():
            if platform.is_dir():
                logger.info(f"Found folder: {self.params['MDDEFolder']}\{platform.name}.")
                for schema in platform.iterdir():