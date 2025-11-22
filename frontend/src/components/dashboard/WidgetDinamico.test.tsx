import React from 'react';
import { render, screen } from '@testing-library/react';
import WidgetDinamico from './WidgetDinamico';
import { ArquetipoInfo } from '@/types';

describe('WidgetDinamico', () => {
  it('renders "Modo Ahorro Energía" for red archetype', () => {
    const mockArquetipo: ArquetipoInfo = {
      nombre: 'El Superviviente',
      color: 'red',
      consejos: []
    };

    render(<WidgetDinamico arquetipo={mockArquetipo} />);
    expect(screen.getByText(/Modo Ahorro Energía/i)).toBeInTheDocument();
  });

  it('renders "Horario Familiar Bloqueado" for orange archetype', () => {
    const mockArquetipo: ArquetipoInfo = {
      nombre: 'El Malabarista',
      color: 'orange',
      consejos: []
    };

    render(<WidgetDinamico arquetipo={mockArquetipo} />);
    expect(screen.getByText(/Horario Familiar Bloqueado/i)).toBeInTheDocument();
  });
});
