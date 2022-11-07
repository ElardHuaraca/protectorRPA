class FilterEnum(enumerate):
    GROUP = ['apagado', 'migrado', 'de_baja', 'pendiente baja',
             'de baja', 'desactivado_temporalmente', 'test', 'migrado', 'historicos', 'migra_veeam']
    SPECIFICATION = ['dia', 'dem', 'demanda', 'crq', 'rfc']
    STATUS = ['aborted', 'failed', 'completed/failures']
    MALFORMED = ['<= /font>', '=font>', '< /font>',
                 '</font>', '&nbsp;', '= font>', '= ', '=']
