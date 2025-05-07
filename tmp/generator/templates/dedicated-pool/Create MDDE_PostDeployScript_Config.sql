DELETE FROM [DA_MDDE].[Config]
WHERE [ModelName] = {% for model in config.Models %}{% if model.IsDocumentModel %}'{{model.Name}}'
{% endif %}{% endfor %}
GO

INSERT INTO [DA_MDDE].[Config] ([ModelName],[LayerName], [EntityName], [MappingName], [MaxTimestamp], [MaxTimestamp_LastRun], [LoadType], [LoadCommand], [LoadRunId], [LoadDateTime], [LoadOutcome])

{%- for mapping in config.Mappings %}                                                              
SELECT  {% for model in config.Models %}{% if model.IsDocumentModel %}'{{model.Name}}'{% endif %}{% endfor %}, 
        '{{mapping.EntityTarget.CodeModel}}', 
        '{{mapping.EntityTarget.Code}}', 
        '{{mapping.Code}}', 
        NULL, 
        NULL, 
        0, 
        'EXEC [DA_MDDE].[sp_LoadEntityData] ''00000000-0000-0000-0000-000000000000'',''{{mapping.EntityTarget.CodeModel}}'',''vw_src_{{mapping.EntityTarget.Code}}_{{mapping.Code}}'', ''{{mapping.EntityTarget.Code}}'',''{{mapping.Code}}'',0', 
        NULL, 
        NULL, 
        NULL
{% if not loop.last %}UNION ALL {% endif %}{% endfor %}
GO 