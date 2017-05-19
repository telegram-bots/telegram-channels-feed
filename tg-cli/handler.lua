print("STARTED HANDLER INITIALISATION")
ROUTING_KEY = "#"
EXCHANGE_NAME = "channels_feed"
HOST = "rabbit"
PORT = 5672

local cjson = require("cjson")
local amqp = require("amqp")
local channel
local opts = {
    mandatory=true
}
local properties = {
    content_type="application/json",
    content_encoding="utf-8",
    delivery_mode=2
}

-- Sleep for given time
function sleep(seconds)
    local sec = tonumber(os.clock() + seconds);
    while (os.clock() < sec) do
    end
end

-- Try to connect to AMQP until success
function connect()
    print("Connecting to AMQP...")

    if channel ~= nil then
        channel:teardown()
        channel = nil
    end

    channel = amqp.new({
        role = "publisher",
        routing_key = ROUTING_KEY,
        exchange = EXCHANGE_NAME,
        mandatory = True
    })

    local conn_ok, conn_err = channel:connect(HOST, PORT)
    while conn_ok == nil do
        print("CONNECTION LOST: " .. conn_err .. ". TRYING TO RECONNECT...")
        sleep(5)
        conn_ok = channel:connect(HOST, PORT)
    end

    local init_ok, init_err = channel:setup()
    while init_ok == nil do
        print("INITIALISATION FAILED: " .. init_err ..  ". TRYING AGAIN...")
        sleep(5)
        init_ok = channel:setup()
    end
    print("Connected to AMQP")
end

connect()
print("HANDLER INITIALISATION COMPLETE")

-- Send message to AMQP exchange
function send_to_exchange(msg)
    local res, err = channel:publish(msg, opts, properties)
    while res ~= true do
        print("Error sending to exchange: " .. err)
        sleep(5)
        if err:find("closed") then
            connect()
        end
        res, err = channel:publish(msg, opts, properties)
    end
    print("Successfully sent to exchange")
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
function dl_cb(arg, data)
end

-- telegram-cli message callback
function tdcli_update_callback(data)
    if (data.ID == "UpdateNewMessage") then
        local msg = data.message_

        if (msg.is_post_ == true) then
            send_to_exchange(cjson.encode(msg))
        elseif msg.content_.ID == "MessageText" then
            if msg.content_.text_:lower() == "ping" then
                reply(msg.chat_id_, msg.id_, "pong")
            end
        end
    end
end
