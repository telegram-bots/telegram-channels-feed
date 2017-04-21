print(">>>>>>>>>>>>>>>>>>> STARTED HANDLER <<<<<<<<<<<<<<<<<")
local encode_json = require("pgmoon.json").encode_json
local pg = require("pgmoon").new({
    host = "db",
    port = "5432",
    database = "postgres",
    user = "postgres"
})
local conn = pg:connect()
print(">>>>>>>>>>>>>>>>>>> INITIALISED HANDLER <<<<<<<<<<<<<<<<<")

-- Sleep for given time
function sleep (seconds)
    local sec = tonumber(os.clock() + seconds);
    while (os.clock() < sec) do
    end
end

-- Try to connect to DB until success
function connect()
    while conn == nil do
        print("CONNECTION LOST. TRYING TO RECONNECT...")
        sleep(5)
        conn = pg:connect()
    end
end

-- Save message to DB
function save_message(chat_id, msg)
    if conn == nil then
        connect()
    end

    local query = "INSERT INTO NewsQueue (channel_telegram_id, payload)"..
            "VALUES(" .. chat_id .. ", " .. encode_json(msg) .. ")"
    local res = pg:query(query)
    while res ~= true do
        print("Error saving to DB")
        if conn == nil then
            connect()
        end
        sleep(5)
        res = pg:query(query)
    end
    print("Successfully saved to DB")
end

-- Reply to user
function reply(chat_id, msg_id, text)
    tdcli_function ({
        ID="SendMessage",
        chat_id_=chat_id,
        reply_to_message_id_=msg_id,
        disable_notification_=0,
        from_background_=1,
        reply_markup_=nil,
        input_message_content_={
            ID="InputMessageText",
            text_=text,
            disable_web_page_preview_=1,
            clear_draft_=0,
            entities_={}
        }
    }, dl_cb, nil)
end

-- telegram-cli default
function dl_cb (arg, data)
end

-- telegram-cli message callback
function tdcli_update_callback (data)
    if (data.ID == "UpdateNewMessage") then
        local msg = data.message_

        if (msg.is_post_ == true) then
            save_message(msg.chat_id_, encode_json(msg))
        elseif msg.content_.ID == "MessageText" then
            if msg.content_.text_:lower() == "ping" then
                reply(msg.chat_id_, msg.id_, "pong")
            end
        end
    end
end
