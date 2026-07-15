import React, {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  App,
  Avatar,
  Button,
  Card,
  Input,
  Space,
  Spin,
  Typography,
} from "antd";

import {
  CloseOutlined,
  MessageOutlined,
  RobotOutlined,
  SendOutlined,
  UserOutlined,
} from "@ant-design/icons";

import axiosClient from "../api/axiosClient";

const { Text } = Typography;

const ChatbotContent = () => {
  const { message } = App.useApp();

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "ai",
      content:
        "Xin chào! Tôi là Trợ lý AI của hệ thống AI Tasker. Tôi có thể giúp bạn tra cứu tiến độ dự án, tìm kiếm chuyên gia hoặc phân tích ngân sách. Bạn cần hỗ trợ gì hôm nay?",
    },
  ]);

  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    const content = inputValue.trim();

    if (!content || isTyping) {
      return;
    }

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        role: "user",
        content,
      },
    ]);

    setInputValue("");
    setIsTyping(true);

    try {
      const response = await axiosClient.post(
        "/chat",
        {
          message: content,
        }
      );

      const reply =
        response.data?.reply ||
        "AI không trả về nội dung phản hồi.";

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "ai",
          content: reply,
        },
      ]);
    } catch (error) {
      console.error(
        "Lỗi gọi API Chatbot:",
        error
      );

      const serverError =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Không thể kết nối tới máy chủ AI.";

      message.error(serverError);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "ai",
          content: `❌ ${serverError}`,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        right: 32,
        bottom: 32,
        zIndex: 9999,
      }}
    >
      {!isOpen && (
        <Button
          type="primary"
          shape="circle"
          size="large"
          aria-label="Mở trợ lý AI"
          icon={
            <MessageOutlined
              style={{
                fontSize: 24,
              }}
            />
          }
          onClick={() => setIsOpen(true)}
          style={{
            width: 60,
            height: 60,
            backgroundColor: "#4f46e5",
            boxShadow:
              "0 10px 25px -5px rgba(79, 70, 229, 0.5)",
          }}
        />
      )}

      {isOpen && (
        <Card
          style={{
            width: 380,
            height: 550,
            borderRadius: 16,
            overflow: "hidden",
            boxShadow:
              "0 20px 25px -5px rgba(0, 0, 0, 0.5)",
            background: "#111827",
            border: "1px solid #1f2937",
          }}
          styles={{
            body: {
              padding: 0,
              display: "flex",
              flexDirection: "column",
              height: "100%",
            },
          }}
        >
          <div
            style={{
              padding: "16px 20px",
              background:
                "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Space>
              <Avatar
                icon={<RobotOutlined />}
                style={{
                  backgroundColor: "#fff",
                  color: "#4f46e5",
                }}
              />

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <Text
                  strong
                  style={{
                    color: "#fff",
                    fontSize: 15,
                  }}
                >
                  AI Enterprise Tasker
                </Text>

                <Text
                  style={{
                    color: "#e0e7ff",
                    fontSize: 11,
                  }}
                >
                  Trực tuyến
                </Text>
              </div>
            </Space>

            <Button
              type="text"
              aria-label="Đóng trợ lý AI"
              icon={
                <CloseOutlined
                  style={{
                    color: "#fff",
                  }}
                />
              }
              onClick={() => setIsOpen(false)}
            />
          </div>

          <div
            style={{
              flex: 1,
              padding: 20,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
          >
            {messages.map((chatMessage, index) => {
              const isUser =
                chatMessage.role === "user";

              return (
                <div
                  key={`${chatMessage.role}-${index}`}
                  style={{
                    display: "flex",
                    flexDirection: isUser
                      ? "row-reverse"
                      : "row",
                    gap: 10,
                    alignItems: "flex-start",
                  }}
                >
                  <Avatar
                    icon={
                      isUser
                        ? <UserOutlined />
                        : <RobotOutlined />
                    }
                    style={{
                      backgroundColor: isUser
                        ? "#1f2937"
                        : "#4f46e5",
                    }}
                  />

                  <div
                    style={{
                      backgroundColor: isUser
                        ? "#4f46e5"
                        : "#1f2937",
                      color: "#fff",
                      padding: "10px 14px",
                      borderRadius: 12,
                      maxWidth: "80%",
                      fontSize: 14,
                      whiteSpace: "pre-wrap",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {chatMessage.content}
                  </div>
                </div>
              );
            })}

            {isTyping && (
              <div
                style={{
                  display: "flex",
                  gap: 10,
                  alignItems: "center",
                }}
              >
                <Avatar
                  icon={<RobotOutlined />}
                  style={{
                    backgroundColor: "#4f46e5",
                  }}
                />

                <Spin size="small" />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div
            style={{
              padding: 16,
              borderTop:
                "1px solid #1f2937",
              background: "#0f172a",
            }}
          >
            <Input
              size="large"
              placeholder="Nhập yêu cầu quản lý..."
              value={inputValue}
              disabled={isTyping}
              onChange={(event) =>
                setInputValue(
                  event.target.value
                )
              }
              onKeyDown={handleKeyDown}
              style={{
                background: "#1f2937",
                border: "none",
                color: "#fff",
              }}
              suffix={
                <Button
                  type="text"
                  aria-label="Gửi tin nhắn"
                  icon={
                    <SendOutlined
                      style={{
                        color:
                          inputValue.trim() &&
                          !isTyping
                            ? "#818cf8"
                            : "#4b5563",
                      }}
                    />
                  }
                  onClick={handleSend}
                  disabled={
                    !inputValue.trim() ||
                    isTyping
                  }
                />
              }
            />
          </div>
        </Card>
      )}
    </div>
  );
};

const EnterpriseChatbot = () => {
  return (
    <App>
      <ChatbotContent />
    </App>
  );
};

export default EnterpriseChatbot;