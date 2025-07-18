# prueba
Prueba de Git para alumno DAM
METHOD zcreate_ovs_filtro_carrid .

  TYPES:
    BEGIN OF lty_stru_input, " filtro
      carrid TYPE s_carr_id,
    END OF lty_stru_input.
  TYPES:
    BEGIN OF lty_stru_list, " Lista del filtro de la tabla
      carrid TYPE s_carr_id,
    END OF lty_stru_list.

  DATA: ls_search_input TYPE lty_stru_input,
        ls_search       TYPE lty_stru_input,
        lt_select_list  TYPE STANDARD TABLE OF lty_stru_list,
        ls_text         TYPE wdr_name_value,
        lt_label_texts  TYPE wdr_name_value_list,
        lt_column_texts TYPE wdr_name_value_list.

  DATA: lo_nd_zwd_filtros TYPE REF TO if_wd_context_node,
        lo_el_zwd_filtros TYPE REF TO if_wd_context_element,
        lo_node_alv       TYPE REF TO if_wd_context_node,
        lt_sflight        TYPE TABLE OF sflight.

  FIELD-SYMBOLS: <ls_query_params>    TYPE lty_stru_input,
                 <ls_selection>       TYPE lty_stru_list,
                 <fs_selection_table> TYPE table.

  CASE ovs_callback_object->phase_indicator.
* Título de la ventana, encabezado de grupo, encabezado de tabla.
    WHEN if_wd_ovs=>co_phase_0.

      " Label
      ls_text-name = 'CARRID'.
      ls_text-value = 'Compañia aérea'.
      INSERT ls_text INTO TABLE lt_label_texts.

      " Las columnas deben coincidir con la estructura de la lista
      " Columnas
      ls_text-name = 'CARRID'.
      ls_text-value = 'Compañia aérea'.
      INSERT ls_text INTO TABLE lt_column_texts.

      ovs_callback_object->set_configuration( label_texts  = lt_label_texts
                                              column_texts = lt_column_texts ).


    WHEN if_wd_ovs=>co_phase_1.
      " Declaracion de busqueda
      CLEAR: ls_search, ls_search_input.

      ovs_callback_object->context_element->get_static_attributes( IMPORTING static_attributes = ls_search_input ).
      ovs_callback_object->set_input_structure( input = ls_search_input ).

    WHEN if_wd_ovs=>co_phase_2.

      DATA(lo_nd_ovs_filters) = wd_context->get_child_node( name = wd_this->wdctx_filtros ).
      DATA(ls_ovs_filters) = VALUE wd_this->element_filtros( ).

      " si el campo CARRID ya tiene un valor en pantalla, necesitamos el carrid para filtrar los resultados.
      lo_nd_ovs_filters->get_static_attributes( IMPORTING static_attributes = ls_ovs_filters ).

      IF ls_ovs_filters-carrid IS NOT INITIAL.
        DELETE lt_sflight WHERE carrid NP ls_ovs_filters-carrid.
      ENDIF.

      " Se trae los datos necesarios de la sflight para tratarlos.
      " Seleccionamos los datos de sflight
      SELECT *
        FROM sflight
        INTO TABLE lt_sflight.

      " Ordenamos y borramos duplicados
      SORT lt_sflight BY carrid.
      DELETE ADJACENT DUPLICATES FROM lt_sflight COMPARING carrid.

      " Introduzco el valor en la tabla que voy a mostrar de la lista con sus datos de carrid y connid
      lt_select_list = VALUE #( FOR ls_datos IN lt_sflight
                      (  carrid = ls_datos-carrid ) ).

      " obtenemos los valores que ha escrito el usuario en la ayuda de busqueda
      ASSIGN ovs_callback_object->query_parameters->* TO <ls_query_params>.

      " Si el filtro recibe un valor de busqueda
      IF <ls_query_params> IS ASSIGNED AND <ls_query_params>-carrid IS NOT INITIAL.
        DELETE lt_select_list WHERE carrid NP <ls_query_params>-carrid.
      ENDIF.

      " Muestra la ayuda de búsqueda en la tabla de resultado
      ovs_callback_object->set_output_table( output = lt_select_list ).

      IF lt_select_list[] IS INITIAL. " Si no tienen ningun registro, error
        MESSAGE e101(zgrc) INTO DATA(lv_msg). " No se han encontrado datos para los criterios seleccionados.
        wd_this->go_message_manager->report_error_message( EXPORTING message_text = lv_msg ).
      ENDIF.

    WHEN if_wd_ovs=>co_phase_3.

      ASSIGN ovs_callback_object->selection->* TO <ls_selection>.
      IF <ls_selection> IS ASSIGNED.
        CLEAR: ls_search.
        ovs_callback_object->context_element->set_attribute(
                               name  = 'CARRID'
                               value = <ls_selection>-carrid ).

      ENDIF.

  ENDCASE.
ENDMETHOD.
