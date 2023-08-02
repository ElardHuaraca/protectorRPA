class FilterEnum(enumerate):
    GROUP = ['apagado', 'migrado', 'baja', 'de_baja', 'pendiente baja', 'de baja',
             'desactivado_temporalmente', 'test', 'historico', 'baja_genesys',
             'default', 'demanda', 'migra_veem_posi', 'reubicacion', 'tarea de baja', 'migrado a commvault']
    SPECIFICATION = ['dia', 'dem', 'demanda', 'crq', 'rfc']
    STATUS = ['aborted', 'failed', 'completed/failures']
    MALFORMED = ['<= /font>', '=font>', '< /font>',
                 '</font>', '&nbsp;', '= font>', '= ', '=']
    PBI = ['group', 'sizeGB', 'reason_status', 'description_status', 'content',
           'frequency', 'environment', 'Duración', 'category_status', 'type']
