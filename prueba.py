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

--------
METHOD onactiongrabar .

  DATA: lo_nd_datos     TYPE REF TO if_wd_context_node,
        lo_nd_datos_aux TYPE REF TO if_wd_context_node,
        lt_elements     TYPE wdr_context_element_set,
        lo_element      TYPE REF TO if_wd_context_element,
        ls_dato         TYPE sflight,
        ls_existente    TYPE sflight.

  " Obtener el nodo
  lo_nd_datos = wd_context->get_child_node( name = wd_this->wdctx_datos_edit ).

  " Hacer un cast al para usar get_elements
  lo_nd_datos_aux ?= lo_nd_datos.

  IF lo_nd_datos_aux IS INITIAL.
    MESSAGE 'No existen datos' TYPE 'E'.
    RETURN.
  ENDIF.

  " Obtener todos los elementos
  lt_elements = lo_nd_datos_aux->get_elements( ).

  LOOP AT lt_elements INTO lo_element.
    CLEAR: ls_dato, ls_existente.

    " Obtener atributos de cada elemento
    lo_element->get_static_attributes( IMPORTING static_attributes = ls_dato ).

    " Validaciones
    IF ls_dato-carrid IS INITIAL OR
       ls_dato-connid IS INITIAL OR
       ls_dato-fldate IS INITIAL.
      MESSAGE 'Deben estar rellenos los campos obligatorios' TYPE 'E'.
    ENDIF.

    " Buscar si el registro ya existe
    SELECT SINGLE *
      INTO ls_existente
      FROM sflight
      WHERE carrid = ls_dato-carrid
        AND connid = ls_dato-connid
        AND fldate = ls_dato-fldate.

    IF sy-subrc = 0.
      " Registro ya existe, actualizamos
      UPDATE sflight FROM ls_dato.
      IF sy-subrc = 0.
        MESSAGE |Registro actualizado: { ls_dato-carrid } { ls_dato-connid } { ls_dato-fldate }| TYPE 'I'.
      ELSE.
        MESSAGE 'Error al actualizar el registro existente' TYPE 'E'.
      ENDIF.
    ELSE.
      " Registro no existe, insertamos
      INSERT sflight FROM ls_dato.
      IF sy-subrc = 0.
        MESSAGE |Nuevo vuelo insertado: { ls_dato-carrid } { ls_dato-connid } { ls_dato-fldate }| TYPE 'I'.
      ELSE.
        MESSAGE 'Error al insertar el nuevo registro' TYPE 'E'.
      ENDIF.
    ENDIF.

  ENDLOOP.

  COMMIT WORK AND WAIT.

  " Volver a la vista principal
  wd_this->fire_out_vista_sec_back_plg( ).
