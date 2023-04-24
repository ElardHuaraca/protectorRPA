class FilterEnum(enumerate):
    GROUP = ['apagado', 'migrado', 'baja', 'de_baja', 'pendiente baja',
             'de baja', 'desactivado_temporalmente', 'test', 'migrado', 'historico', 'migra_veeam']
    SPECIFICATION = ['dia', 'dem', 'demanda', 'crq', 'rfc']
    STATUS = ['aborted', 'failed', 'completed/failures']
    MALFORMED = ['<= /font>', '=font>', '< /font>',
                 '</font>', '&nbsp;', '= font>', '= ', '=']
    PBI = ['group', 'sizeGB', 'reason_status', 'description_status','content', 'frequency', 'environment']