import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const getArtifact = vi.fn()

vi.mock('../api/client', () => ({
  apiClient: {
    getArtifact: (...args: unknown[]) => getArtifact(...args),
  },
}))

vi.mock('mermaid', () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn().mockResolvedValue({ svg: '<svg />' }),
  },
}))

import { ArtifactsViewer } from './ArtifactsViewer'

describe('ArtifactsViewer', () => {
  beforeEach(() => {
    getArtifact.mockReset()
    getArtifact.mockImplementation((runId: string, artifactName: string) => {
      if (artifactName === 'canonical') {
        return Promise.resolve({
          content: {
            interfaces: [
              {
                id: 'if-1',
                name: 'User API',
                threats: [
                  {
                    id: 'th-1',
                    name: 'Injection threat',
                    description: 'Untrusted input reaches the backend handler.',
                    likelihood: 4,
                    impact: 5,
                    capec_id: 'CAPEC-78',
                    cwe_id: 'CWE-79',
                  },
                ],
              },
            ],
          },
        })
      }

      if (artifactName === 'mermaid') {
        return Promise.resolve({ content: { diagrams: [] } })
      }

      return Promise.resolve({ content: { runId, artifactName } })
    })
  })

  it('renders threat rows inside the Artifacts threat subview', async () => {
    const user = userEvent.setup()

    render(<ArtifactsViewer runId="run-123" initialTab={0} />)

    await waitFor(() => expect(getArtifact).toHaveBeenCalled())
    await user.click(screen.getByRole('tab', { name: /Threats/ }))

    expect(screen.getByText('Injection threat')).toBeInTheDocument()
    expect(screen.getByText('Interface: User API')).toBeInTheDocument()
    expect(screen.getByText('Untrusted input reaches the backend handler.')).toBeInTheDocument()
    expect(screen.getByText('Likelihood 4')).toBeInTheDocument()
    expect(screen.getByText('Impact 5')).toBeInTheDocument()
    expect(screen.getByText('CAPEC-78')).toBeInTheDocument()
    expect(screen.getByText('CWE-79')).toBeInTheDocument()
  })
})
