print("Ande esta er betis")
print("beti viva er beti")

 DATA: lo_nd_datos     TYPE REF TO if_wd_context_node,
        lo_nd_datos_aux TYPE REF TO if_wd_context_node,
        lt_elements     TYPE wdr_context_element_set,
        lo_element      TYPE REF TO if_wd_context_element,
        ls_dato         TYPE sflight.

  " Obtener el nodo
  lo_nd_datos = wd_context->get_child_node( name = wd_this->wdctx_datos_edit ).

  " Hacer un cast a nodo tabla para poder usar get_elements
  lo_nd_datos_aux ?= lo_nd_datos.

  IF lo_nd_datos_aux IS INITIAL.
    MESSAGE 'No existen datos' TYPE 'E'.
    RETURN.
  ENDIF.

  " Obtener todos los elementos
  lt_elements = lo_nd_datos_aux->get_elements( ).

  LOOP AT lt_elements INTO lo_element.
    CLEAR ls_dato.

    " Obtener atributos de cada elemento
    lo_element->get_static_attributes( IMPORTING static_attributes = ls_dato ).

    " Validaciones
    IF ls_dato-carrid IS INITIAL OR
       ls_dato-connid IS INITIAL OR
       ls_dato-fldate IS INITIAL.
      MESSAGE 'Deben estan rellenos los campos son obligatorios' TYPE 'E'.
    ENDIF.

    " Verificar si el registro ya existe
    SELECT SINGLE *
      FROM sflight
      INTO @DATA(ls_existente)
      WHERE carrid EQ @ls_dato-carrid
        AND connid EQ @ls_dato-connid
        AND fldate EQ @ls_dato-fldate.


    IF sy-subrc EQ 0.
      " Registro existe
      MESSAGE |Ya existe un vuelo con la misma clave: { ls_dato-carrid } { ls_dato-connid } { ls_dato-fldate }| TYPE 'E'.
      EXIT.
    ENDIF.

    " Nuevo registro de vuelo
    MODIFY sflight FROM ls_dato.
    IF sy-subrc EQ 0.
      MESSAGE 'Se ha actualizado la tabla sflight' TYPE 'I'.
    ENDIF.

  ENDLOOP.

  COMMIT WORK AND WAIT.

  " Volver a la vista principal
  wd_this->fire_out_vista_sec_back_plg( ).
