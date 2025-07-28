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
--
METHOD wddoinit .

  DATA: lo_cmp_usage       TYPE REF TO if_wd_component_usage,
        lo_salv_wd_table   TYPE REF TO iwci_salv_wd_table,
        lo_column_settings TYPE REF TO if_salv_wd_column_settings,
        lo_column          TYPE REF TO cl_salv_wd_column,
        lt_column          TYPE salv_wd_t_column_ref,
        ls_column          TYPE salv_wd_s_column_ref,
        lo_column_header   TYPE REF TO cl_salv_wd_column_header,
        lr_config          TYPE REF TO cl_salv_wd_config_table,
        l_table            TYPE salv_t_column_ref.

*    Creamos el componente ALV
  lo_cmp_usage = wd_this->wd_cpuse_alv_principal( ).

  " Si no está creado, lo creamos
  IF lo_cmp_usage->has_active_component( ) IS INITIAL.
    lo_cmp_usage->create_component( ).
  ENDIF.

  " Recuperamos el componente ALV
  lo_salv_wd_table = wd_this->wd_cpifc_alv_principal( ).
  lr_config = lo_salv_wd_table->get_model( ).
  lr_config->if_salv_wd_table_settings~set_cell_action_event_enabled( abap_true ).
  lo_salv_wd_table->get_model( )->if_salv_wd_table_settings~set_visible_row_count( '30' ).
  lo_column_settings ?= lo_salv_wd_table->get_model( ).

  " Recuperamos las columnas
  lt_column = lo_column_settings->get_columns( ).

  LOOP AT lt_column INTO ls_column.
    lo_column = lr_config->if_salv_wd_column_settings~get_column( id = ls_column-id ).
    CASE ls_column-id.

        " Configurar todos los campos del ALV
      WHEN 'MANDT'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_none ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Mandante' ).

      WHEN 'CARRID'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Compañia aérea' ).

      WHEN 'CONNID'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Cod. conexión de vuelo directo' ).

      WHEN 'FLDATE'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Fecha de vuelo' ).

      WHEN 'PRICE'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Precio del vuelo' ).

      WHEN 'CURRENCY'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Moneda local de la compañía aérea' ).

      WHEN 'PLANETYPE'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Tipo de avión' ).

      WHEN 'SEATSMAX'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Ocupación máxima en clase económica' ).
      WHEN 'SEATSOCC'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Plazas ocupadas en clase económica' ).
      WHEN 'PAYMENTSUM'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Total reservas efectuadas hasta el momento' ).
      WHEN 'SEATSMAX_B'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Ocupación máxima en clase Business' ).

      WHEN 'SEATSOCC_B'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Plazas ocupada en clase Business' ).
      WHEN 'SEATSMAX_F'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Ocupación máxima en primera clase' ).
      WHEN 'SEATSOCC_F'.
        ls_column-r_column->set_visible( if_wdl_core=>visibility_visible ).
        lo_column_header = ls_column-r_column->get_header( ).
        lo_column_header->set_ddic_binding_field( if_salv_wd_c_column_settings=>ddic_bind_none ).
        lo_column_header->set_text( 'Plazas ocupadas en primera clase' ).

    ENDCASE.
  ENDLOOP.

ENDMETHOD.
