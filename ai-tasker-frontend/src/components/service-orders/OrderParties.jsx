import React, { useMemo } from "react";

import {
  Avatar,
  Button,
  Card,
  Col,
  Descriptions,
  Divider,
  Empty,
  Flex,
  Row,
  Space,
  Tag,
  Typography,
} from "antd";

import {
  EnvironmentOutlined,
  MailOutlined,
  PhoneOutlined,
  ShopOutlined,
  UserOutlined,
} from "@ant-design/icons";


const {
  Text,
  Title,
  Paragraph,
} = Typography;


// ==========================================================
// HELPERS
// ==========================================================

const getDisplayName = (
  entity,
  fallback
) => (
  entity?.name
  || entity?.full_name
  || entity?.company_name
  || entity?.username
  || fallback
);


const getAvatarSource = (entity) => (
  entity?.avatar_url
  || entity?.avatar
  || entity?.image_url
  || entity?.logo_url
  || null
);


const formatCurrency = (
  value,
  currency = "VND"
) => {
  const numericValue = Number(value || 0);

  if (!Number.isFinite(numericValue)) {
    return `0 ${currency}`;
  }

  try {
    return new Intl.NumberFormat(
      "vi-VN",
      {
        style: "currency",
        currency: currency || "VND",
        maximumFractionDigits: 0,
      }
    ).format(numericValue);
  } catch {
    return (
      `${numericValue.toLocaleString("vi-VN")} `
      + `${currency || "VND"}`
    );
  }
};


const InformationRow = ({
  icon,
  label,
  value,
}) => {
  if (
    value === null
    || value === undefined
    || value === ""
  ) {
    return null;
  }

  return (
    <Flex
      align="flex-start"
      gap={10}
    >
      <span
        style={{
          color: "#818cf8",
          marginTop: 2,
        }}
      >
        {icon}
      </span>

      <div>
        <Text
          type="secondary"
          style={{
            display: "block",
            fontSize: 12,
          }}
        >
          {label}
        </Text>

        <Text>
          {value}
        </Text>
      </div>
    </Flex>
  );
};


// ==========================================================
// ENTERPRISE CARD
// ==========================================================

function EnterpriseCard({
  enterprise,
  enterpriseId,
  onViewEnterprise,
}) {
  const displayName = getDisplayName(
    enterprise,
    "Doanh nghiệp"
  );

  const avatarSource = getAvatarSource(
    enterprise
  );

  return (
    <Card
      title={
        <Space>
          <ShopOutlined />
          <span>Doanh nghiệp đặt dịch vụ</span>
        </Space>
      }
      style={{
        height: "100%",
      }}
      extra={
        typeof onViewEnterprise
          === "function" && (
          <Button
            type="link"
            onClick={() => {
              onViewEnterprise(
                enterprise?.id
                || enterpriseId
              );
            }}
          >
            Xem hồ sơ
          </Button>
        )
      }
    >
      <Flex
        align="center"
        gap={16}
      >
        <Avatar
          size={64}
          shape="square"
          src={avatarSource}
          icon={<ShopOutlined />}
          style={{
            background:
              "linear-gradient(135deg, #0891b2, #2563eb)",
          }}
        />

        <div
          style={{
            flex: 1,
            minWidth: 0,
          }}
        >
          <Title
            level={4}
            ellipsis
            style={{
              margin: 0,
            }}
          >
            {displayName}
          </Title>

          <Text type="secondary">
            {enterprise?.industry
              || enterprise?.business_type
              || "Khách hàng doanh nghiệp"}
          </Text>
        </div>
      </Flex>

      <Divider />

      <Space
        direction="vertical"
        size={14}
        style={{
          width: "100%",
        }}
      >
        <InformationRow
          icon={<MailOutlined />}
          label="Email"
          value={enterprise?.email}
        />

        <InformationRow
          icon={<PhoneOutlined />}
          label="Số điện thoại"
          value={
            enterprise?.phone
            || enterprise?.phone_number
          }
        />

        <InformationRow
          icon={<EnvironmentOutlined />}
          label="Địa chỉ"
          value={
            enterprise?.address
            || enterprise?.location
          }
        />
      </Space>

      {enterprise?.description && (
        <>
          <Divider />

          <Paragraph
            type="secondary"
            ellipsis={{
              rows: 4,
              expandable: true,
              symbol: "Xem thêm",
            }}
            style={{
              marginBottom: 0,
              lineHeight: 1.7,
            }}
          >
            {enterprise.description}
          </Paragraph>
        </>
      )}

      {!enterprise && enterpriseId && (
        <>
          <Divider />

          <Descriptions
            bordered
            size="small"
            column={1}
          >
            <Descriptions.Item
              label="Enterprise ID"
            >
              <Text copyable>
                {enterpriseId}
              </Text>
            </Descriptions.Item>
          </Descriptions>
        </>
      )}
    </Card>
  );
}


// ==========================================================
// EXPERT CARD
// ==========================================================

function ExpertCard({
  expert,
  expertId,
  currency,
  onViewExpert,
}) {
  const displayName = getDisplayName(
    expert,
    "Chuyên gia AI"
  );

  const avatarSource = getAvatarSource(
    expert
  );

  const skills = useMemo(
    () => (
      Array.isArray(expert?.skills)
        ? expert.skills
        : []
    ),
    [expert]
  );

  return (
    <Card
      title={
        <Space>
          <UserOutlined />
          <span>Chuyên gia thực hiện</span>
        </Space>
      }
      style={{
        height: "100%",
      }}
      extra={
        typeof onViewExpert
          === "function" && (
          <Button
            type="link"
            onClick={() => {
              onViewExpert(
                expert?.id || expertId
              );
            }}
          >
            Xem hồ sơ
          </Button>
        )
      }
    >
      <Flex
        align="center"
        gap={16}
      >
        <Avatar
          size={64}
          src={avatarSource}
          icon={<UserOutlined />}
          style={{
            background:
              "linear-gradient(135deg, #4f46e5, #7c3aed)",
          }}
        />

        <div
          style={{
            flex: 1,
            minWidth: 0,
          }}
        >
          <Title
            level={4}
            ellipsis
            style={{
              margin: 0,
            }}
          >
            {displayName}
          </Title>

          <Text type="secondary">
            {expert?.title
              || "AI Expert"}
          </Text>
        </div>
      </Flex>

      <Divider />

      <Space
        direction="vertical"
        size={14}
        style={{
          width: "100%",
        }}
      >
        <InformationRow
          icon={<MailOutlined />}
          label="Email"
          value={expert?.email}
        />

        <InformationRow
          icon={<PhoneOutlined />}
          label="Số điện thoại"
          value={
            expert?.phone
            || expert?.phone_number
          }
        />

        <InformationRow
          icon={<EnvironmentOutlined />}
          label="Khu vực"
          value={expert?.location}
        />
      </Space>

      {expert?.hourly_rate !== null
        && expert?.hourly_rate !== undefined && (
        <>
          <Divider />

          <Descriptions
            bordered
            size="small"
            column={1}
          >
            <Descriptions.Item
              label="Đơn giá theo giờ"
            >
              <Text strong>
                {formatCurrency(
                  expert.hourly_rate,
                  currency || "VND"
                )}
              </Text>
            </Descriptions.Item>
          </Descriptions>
        </>
      )}

      {skills.length > 0 && (
        <>
          <Divider />

          <Text
            strong
            style={{
              display: "block",
              marginBottom: 10,
            }}
          >
            Kỹ năng
          </Text>

          <Flex
            gap={7}
            wrap="wrap"
          >
            {skills
              .slice(0, 8)
              .map((skill, index) => {
                const label = (
                  typeof skill === "string"
                    ? skill
                    : skill?.name
                      || skill?.title
                      || "Skill"
                );

                return (
                  <Tag
                    key={`${label}-${index}`}
                    color="blue"
                    style={{
                      marginInlineEnd: 0,
                      borderRadius: 999,
                    }}
                  >
                    {label}
                  </Tag>
                );
              })}

            {skills.length > 8 && (
              <Tag>
                +{skills.length - 8}
              </Tag>
            )}
          </Flex>
        </>
      )}

      {expert?.bio && (
        <>
          <Divider />

          <Paragraph
            type="secondary"
            ellipsis={{
              rows: 4,
              expandable: true,
              symbol: "Xem thêm",
            }}
            style={{
              marginBottom: 0,
              lineHeight: 1.7,
            }}
          >
            {expert.bio}
          </Paragraph>
        </>
      )}

      {!expert && expertId && (
        <>
          <Divider />

          <Descriptions
            bordered
            size="small"
            column={1}
          >
            <Descriptions.Item
              label="Expert ID"
            >
              <Text copyable>
                {expertId}
              </Text>
            </Descriptions.Item>
          </Descriptions>
        </>
      )}
    </Card>
  );
}


// ==========================================================
// MAIN COMPONENT
// ==========================================================

function OrderParties({
  order,
  onViewEnterprise,
  onViewExpert,
}) {
  const enterprise = useMemo(
    () => order?.enterprise || null,
    [order]
  );

  const expert = useMemo(
    () => order?.expert || null,
    [order]
  );

  if (!order) {
    return (
      <Card>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            "Không có dữ liệu các bên tham gia."
          }
        />
      </Card>
    );
  }

  return (
    <Row
      gutter={[24, 24]}
      style={{
        marginTop: 24,
      }}
    >
      <Col
        xs={24}
        lg={12}
      >
        <EnterpriseCard
          enterprise={enterprise}
          enterpriseId={
            order.enterprise_id
          }
          onViewEnterprise={
            onViewEnterprise
          }
        />
      </Col>

      <Col
        xs={24}
        lg={12}
      >
        <ExpertCard
          expert={expert}
          expertId={order.expert_id}
          currency={order.currency}
          onViewExpert={onViewExpert}
        />
      </Col>
    </Row>
  );
}


export default OrderParties;