import React from 'react';
import { Form, Select, InputNumber, DatePicker, Button, Radio } from 'antd';
import { Calculator } from 'lucide-react';
import dayjs from 'dayjs';
import type { Fund } from '../types';

const { RangePicker } = DatePicker;

interface FundFormProps {
  funds: Fund[];
  loading: boolean;
  onSubmit: (values: {
    fund_code: string;
    amount: number;
    frequency: 'monthly' | 'weekly';
    start_date: string;
    end_date: string;
  }) => void;
  submitting: boolean;
}

const FundForm: React.FC<FundFormProps> = ({ funds, loading, onSubmit, submitting }) => {
  const [form] = Form.useForm();

  const handleFinish = (values: {
    fund_code: string;
    amount: number;
    frequency: 'monthly' | 'weekly';
    dateRange: [dayjs.Dayjs, dayjs.Dayjs];
  }) => {
    onSubmit({
      fund_code: values.fund_code,
      amount: values.amount,
      frequency: values.frequency,
      start_date: values.dateRange[0].format('YYYY-MM-DD'),
      end_date: values.dateRange[1].format('YYYY-MM-DD'),
    });
  };

  const selectedFund = Form.useWatch('fund_code', form);
  const selectedFundData = funds.find((f) => f.code === selectedFund);

  const disabledDate = (current: dayjs.Dayjs) => {
    if (!selectedFundData) return false;
    return (
      current.isBefore(dayjs(selectedFundData.min_date)) ||
      current.isAfter(dayjs(selectedFundData.max_date))
    );
  };

  return (
    <div className="fund-form">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{
          amount: 1000,
          frequency: 'monthly',
        }}
      >
        <Form.Item
          name="fund_code"
          label="选择基金"
          rules={[{ required: true, message: '请选择基金' }]}
        >
          <Select
            placeholder="请选择基金"
            loading={loading}
            options={funds.map((fund) => ({
              value: fund.code,
              label: `${fund.code} - ${fund.name}`,
            }))}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        </Form.Item>

        <Form.Item
          name="amount"
          label="每期定投金额"
          rules={[
            { required: true, message: '请输入定投金额' },
            { type: 'number', min: 1, message: '金额必须大于0' },
          ]}
        >
          <InputNumber
            min={1}
            style={{ width: '100%' }}
            addonAfter="元"
            precision={0}
          />
        </Form.Item>

        <Form.Item
          name="frequency"
          label="定投频率"
          rules={[{ required: true, message: '请选择定投频率' }]}
        >
          <Radio.Group>
            <Radio.Button value="monthly">每月定投</Radio.Button>
            <Radio.Button value="weekly">每周定投</Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Form.Item
          name="dateRange"
          label="定投期间"
          rules={[{ required: true, message: '请选择定投期间' }]}
        >
          <RangePicker
            style={{ width: '100%' }}
            disabledDate={disabledDate}
            format="YYYY-MM-DD"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={submitting}
            icon={<Calculator size={16} />}
            block
          >
            开始回测
          </Button>
        </Form.Item>
      </Form>

      {selectedFundData && (
        <div className="fund-info">
          <span className="fund-info-label">可用净值日期范围：</span>
          <span>
            {selectedFundData.min_date} 至 {selectedFundData.max_date}
          </span>
        </div>
      )}
    </div>
  );
};

export default FundForm;