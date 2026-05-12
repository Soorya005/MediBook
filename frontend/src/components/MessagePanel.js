import React, { useState } from 'react';
import { messageAPI } from '../utils/api';

const MessagePanel = ({ messages, onRefresh }) => {
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;

    setLoading(true);
    try {
      await messageAPI.send({
        content: newMessage,
        recipient_id: selectedConversation,
        message_type: 'text',
      });
      setNewMessage('');
      onRefresh();
    } catch (error) {
      alert('Error sending message: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const conversationIds = [...new Set(messages.flatMap((m) => [m.sender_id, m.recipient_id]))];

  return (
    <div className="card">
      <div className="card-header">
        <h3>Messages</h3>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem' }}>
        <div>
          <h4>Conversations</h4>
          {conversationIds.length === 0 ? (
            <p className="text-muted">No messages yet</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {conversationIds.map((id) => (
                <button
                  key={id}
                  className={selectedConversation === id ? '' : 'secondary'}
                  onClick={() => setSelectedConversation(id)}
                  style={{ textAlign: 'left', padding: '0.5rem' }}
                >
                  User ID: {id}
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          {selectedConversation ? (
            <div>
              <h4>Conversation</h4>
              <div style={{ 
                backgroundColor: '#f9f9f9', 
                padding: '1rem', 
                borderRadius: '4px', 
                minHeight: '300px',
                maxHeight: '400px',
                overflowY: 'auto',
                marginBottom: '1rem'
              }}>
                {messages
                  .filter((m) => m.sender_id === selectedConversation || m.recipient_id === selectedConversation)
                  .map((msg) => (
                    <div key={msg.id} style={{ marginBottom: '0.5rem' }}>
                      <strong>{msg.sender_id === selectedConversation ? 'Other' : 'You'}:</strong> {msg.content}
                      <p style={{ fontSize: '12px', color: '#999' }}>
                        {new Date(msg.created_at).toLocaleString()}
                      </p>
                    </div>
                  ))}
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <button onClick={handleSendMessage} disabled={loading}>
                  Send
                </button>
              </div>
            </div>
          ) : (
            <p className="text-muted">Select a conversation to view messages</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessagePanel;
