CREATE VIEW [{{mapping.EntityTarget.CodeModel}}].[vw_src_{{mapping.EntityTarget.Code}}_{{mapping.DataSource}}]
AS SELECT
{% set sqlexpression = {
    'AVERAGE': 'AVG',
    'COUNT': 'COUNT',
    'MAXIMUM': 'MAX',
    'MINIMUM': 'MIN',
    'SUM': 'SUM' } -%}
{% for attributemapping in mapping.AttributeMapping %}
{% if 'Expression' in attributemapping %}[{{attributemapping.AttributeTarget.Code}}]  = {{sqlexpression.get(attributemapping.Expression)}}({{attributemapping.AttributesSource.IdEntity}}.[{{attributemapping.AttributesSource.Name}}])
{% elif Expression not in attributemapping %}[{{attributemapping.AttributeTarget.Code}}]  = {{attributemapping.AttributesSource.IdEntity}}.[{{attributemapping.AttributesSource.Name}}]
{% endif %}
{%- if not loop.last -%}, {% endif %}
{% endfor %}
{% for sourceObject in mapping.SourceComposition %}
{% if sourceObject.JoinType != 'APPLY' %}{{ sourceObject.JoinType}} {{sourceObject.Entity.CodeModel}}.{{sourceObject.Entity.Name}} AS {{sourceObject.Entity.Id}} 
{% if 'JoinConditions' in sourceObject %}ON 
{% for joinCondition in sourceObject.JoinConditions %}
{% if joinCondition.ParentLiteral != '' %}{{sourceObject.JoinAlias}} .{{joinCondition.JoinConditionComponents.AttributeChild.Name}} = {{joinCondition.ParentLiteral}}
{% elif joinCondition.ParentLiteral == '' %}{{sourceObject.JoinAlias}} .{{joinCondition.JoinConditionComponents.AttributeChild.Name}} = {{joinCondition.JoinConditionComponents.AttributeParent.EntityAlias}}.{{joinCondition.JoinConditionComponents.AttributeParent.Name}} 
{% endif %}
{%- if not loop.last -%} AND {% endif %}
{% endfor %}
{% endif %}
{% endif %}    
{% endfor %}
GROUP BY
{% for attributemapping in mapping.AttributeMapping %}
{% if 'Expression' not in attributemapping and not loop.first%},{{attributemapping.AttributesSource.IdEntity}}.[{{attributemapping.AttributesSource.Name}}]
{% elif 'Expression' not in attributemapping%}{{attributemapping.AttributesSource.IdEntity}}.[{{attributemapping.AttributesSource.Name}}]
{% endif %}
{% endfor %}
;
