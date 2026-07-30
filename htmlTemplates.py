css = '''
<style>
.chat-container {
    max-height: 500px;      
    overflow-y: auto;      
    border: 1px solid #ccc;
    border-radius: 0.5rem;
    padding: 1rem;
    background-color: #ffffff;
}
.chat-message {
    margin-bottom: 1rem;
    display: flex;
}
.chat-message.user {
    justify-content: flex-end;   
}
.chat-message.bot {
    justify-content: flex-start;   
}
.chat-message.user .message {
    background-color: #dcf8c6;   
    color: #000;
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    max-width: 70%;
}
.chat-message.bot .message {
    background-color: transparent;
    color: #000;
    padding: 0.5rem 0;
    max-width: 70%;
}
.source{
    font-size: 0.8rem;
    color: #888;
    font-style: italic;
    margin-top: 0.25rem;
    margin-left: 0.5rem;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
</div>
'''
