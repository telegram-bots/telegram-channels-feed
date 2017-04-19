print(">>>>>>>>>>>>>>>>>>>>>CALLED AGAIN AND AGAIN<<<<<<<<<<<<<<<<<<<<<<<<<<")

function dl_cb (arg, data)
end

function tdcli_update_callback (data)
    if (data.ID == "UpdateNewMessage") then
        local msg = data.message_

        if (msg.is_post_ == true) then
            print(msg.content_.text_)
        end

        if msg.content_.ID == "MessageText" then
            if msg.content_.text_ == "ping" then
                tdcli_function ({ID="SendMessage", chat_id_=msg.chat_id_, reply_to_message_id_=msg.id_, disable_notification_=0, from_background_=1, reply_markup_=nil, input_message_content_={ID="InputMessageText", text_="pong", disable_web_page_preview_=1, clear_draft_=0, entities_={}}}, dl_cb, nil)
            elseif msg.content_.text_ == "PING" then
                tdcli_function ({ID="SendMessage", chat_id_=msg.chat_id_, reply_to_message_id_=msg.id_, disable_notification_=0, from_background_=1, reply_markup_=nil, input_message_content_={ID="InputMessageText", text_="pong", disable_web_page_preview_=1, clear_draft_=0, entities_={[0]={ID="MessageEntityBold", offset_=0, length_=4}}}}, dl_cb, nil)
            end
        end
    end
end
