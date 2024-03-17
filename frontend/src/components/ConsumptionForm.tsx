import React from 'react'
import Switch from './Switch';

interface Props {
    date: Date | null;
    setDate: React.Dispatch<React.SetStateAction<Date | null>>;
    form: State;
    setForm: React.Dispatch<React.SetStateAction<Record<string, State>>>;
    selectedForm: 'Morning' | 'Afternoon' | 'Night';
  }

export interface State {
  gas: number;
  electricity: number;
  water: number;
  temperature: number;
  atHome: boolean;
  date: string;
  timeslot: 'Morning' | 'Afternoon' | 'Night';
}

class ConsumptionForm extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    const { date } = props;
  }

  handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const newValue = name === 'atHome' ? e.target.checked : parseFloat(value);
  
    if (name === 'date') {
      const newDate = new Date(value);
      this.props.setDate(newDate);
      this.props.setForm((prevForms) => {
        const newForms = { ...prevForms };
        for (const formKey in newForms) {
          newForms[formKey] = { ...newForms[formKey], date: newDate.toISOString().split('T')[0] };
        }
        return newForms;
      });
    } else {
      this.props.setForm((prevForms) => ({
        ...prevForms,
        [this.props.selectedForm]: { ...prevForms[this.props.selectedForm], [name]: newValue },
      }));
    }
  };
  
  

  handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("Submitting " + this.props.selectedForm + " form: " + JSON.stringify(this.props.form));

    const token = localStorage.getItem('token');
    fetch('http://localhost:5000/consumption', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(this.props.form)
    }).then((response) => {
      if (response.ok) {
        console.log("Form submitted successfully");
      } else {
        console.log("Error:", response.status);
      }
    });
  };


  render() {
    const { date, setDate, form, setForm } = this.props;
    return (
      <form onSubmit={this.handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between border p-4 rounded bg-white">
          <label htmlFor="gas" className="w-24 font-bold">Gas</label>
          <input type="number" name="gas" id="gas" value={form.gas} onChange={this.handleInputChange} className="flex-1 ml-2 text-right" />
          <span className="ml-2 w-16 text-right">m³</span>
        </div>
        <div className="flex items-center justify-between border p-4 rounded bg-white">
          <label htmlFor="electricity" className="w-24 font-bold">Electricity</label>
          <input type="number" name="electricity" id="electricity" value={form.electricity} onChange={this.handleInputChange} className="flex-1 ml-2 text-right" />
          <span className="ml-2 w-16 text-right">kWh</span>
        </div>
        <div className="flex items-center justify-between border p-4 rounded bg-white">
          <label htmlFor="water" className="w-24 font-bold">Water</label>
          <input type="number" name="water" id="water" value={form.water} onChange={this.handleInputChange} className="flex-1 ml-2 text-right" />
          <span className="ml-2 w-16 text-right">L</span>
        </div>
        <div className="flex items-center justify-between border p-4 rounded bg-white">
          <label htmlFor="temperature" className="w-24 font-bold">Outside Temperature</label>
          <input type="number" name="temperature" id="temperature" value={form.temperature} onChange={this.handleInputChange} className="flex-1 ml-2 text-right" />
          <span className="ml-2 w-16 text-right">°C</span>
        </div>
        <div className="flex items-center justify-between border p-4 rounded bg-white">
          <label htmlFor="atHome" className="w-24 font-bold">At home?</label>
          {/* <input type="checkbox" name="atHome" id="atHome" onChange={this.handleInputChange} className="flex-1 ml-2 text-right" /> */}
          <Switch
            name="atHome"
            id="atHome"
            checked={form.atHome}
            onChange={this.handleInputChange}
          />
        </div>
        <div className="flex items-center justify-between border p-4 rounded bg-white">
        <label htmlFor="date" className="w-24 font-bold">Date</label>
        <input
            type="date"
            name="date"
            id="date"
            value={date ? date.toISOString().split('T')[0] : ''}
            onChange={(e) => {
                setDate(new Date(e.target.value));
                this.handleInputChange(e);
            }}
            className="flex-1 ml-2 text-right"
        />
        </div>
        <div className="flex justify-center mt-4">
            <button type="submit" className="py-2 px-11 bg-blue-500 text-white rounded-lg font-bold">Submit</button>
        </div>
      </form>
    );
  }
}

export default ConsumptionForm;
