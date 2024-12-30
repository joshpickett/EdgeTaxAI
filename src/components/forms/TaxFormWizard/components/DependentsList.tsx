import React from 'react';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface Dependent {
  id: string;
  firstName: string;
  lastName: string;
  ssn: string;
  relationship: string;
  monthsLived: number;
  birthdate: string;
}

interface DependentsListProps {
  dependents: Dependent[];
  onUpdate: (dependents: Dependent[]) => void;
}

export const DependentsList: React.FC<DependentsListProps> = ({
  dependents,
  onUpdate
}) => {
  const handleAddDependent = () => {
    const newDependent: Dependent = {
      id: `dep_${Date.now()}`,
      firstName: '',
      lastName: '',
      ssn: '',
      relationship: '',
      monthsLived: 12,
      birthdate: ''
    };
    onUpdate([...dependents, newDependent]);
  };

  const handleDependentChange = (id: string, field: keyof Dependent, value: any) => {
    const updatedDependents = dependents.map(dep =>
      dep.id === id ? { ...dep, [field]: value } : dep
    );
    onUpdate(updatedDependents);
  };

  const handleRemoveDependent = (id: string) => {
    onUpdate(dependents.filter(dep => dep.id !== id));
  };

  return (
    <div style={formSectionStyles.container}>
      {dependents.map(dependent => (
        <div key={dependent.id} style={formFieldStyles.group}>
          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>First Name</label>
              <input
                type="text"
                value={dependent.firstName}
                onChange={(e) => handleDependentChange(dependent.id, 'firstName', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Last Name</label>
              <input
                type="text"
                value={dependent.lastName}
                onChange={(e) => handleDependentChange(dependent.id, 'lastName', e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
          </div>

          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>SSN</label>
              <input
                type="text"
                value={dependent.ssn}
                onChange={(e) => handleDependentChange(dependent.id, 'ssn', e.target.value)}
                style={formFieldStyles.input}
                pattern="\d{3}-?\d{2}-?\d{4}"
                placeholder="XXX-XX-XXXX"
              />
            </div>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Relationship</label>
              <select
                value={dependent.relationship}
                onChange={(e) => handleDependentChange(dependent.id, 'relationship', e.target.value)}
                style={formFieldStyles.select}
              >
                <option value="">Select Relationship</option>
                <option value="child">Child</option>
                <option value="stepchild">Stepchild</option>
                <option value="sibling">Sibling</option>
                <option value="parent">Parent</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <button
            onClick={() => handleRemoveDependent(dependent.id)}
            style={formFieldStyles.button.secondary}
          >
            Remove Dependent
          </button>
        </div>
      ))}

      <button
        onClick={handleAddDependent}
        style={formFieldStyles.button.primary}
      >
        Add Dependent
      </button>
    </div>
  );
};
