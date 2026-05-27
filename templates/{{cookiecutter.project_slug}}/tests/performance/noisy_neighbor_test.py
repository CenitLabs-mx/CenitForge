"""
Noisy-Neighbor Test V5
Verifica que un tenant con alta carga no degrada la latencia de otros tenants.
Obligatorio en M2+ para todo endpoint que acepta input de tenant.
"""

from __future__ import annotations

import concurrent.futures
import time
from typing import Callable, List

import numpy as np
import pytest


# ------------------------------------------------------------
# Fixtures / helpers (adaptar al proyecto real)
# ------------------------------------------------------------

def create_test_tenant(name: str) -> "Tenant":
    """Crea un tenant de prueba en staging."""
    # Implementación real: API call a staging
    class Tenant:
        def __init__(self, tid, n):
            self.id = tid
            self.name = n
    return Tenant(tid=f"tenant-{name}-{int(time.time())}", n=name)


def make_heavy_request(tenant_id: str) -> dict:
    """Request pesado: paginación grande, joins, etc."""
    # TODO: reemplazar con llamada real al endpoint
    time.sleep(0.01)
    return {"ok": True, "tenant": tenant_id}


def make_normal_request(tenant_id: str) -> dict:
    """Request ligero de referencia."""
    time.sleep(0.005)
    return {"ok": True, "tenant": tenant_id}


# ------------------------------------------------------------
# Test principal
# ------------------------------------------------------------

class TestNoisyNeighbor:
    """
    Garantiza que el aislamiento multi-tenant funciona bajo carga.
    """

    BASELINE_P95_MS = 500     # 500 ms p95 objetivo
    CONCURRENT_HEAVY = 50     # requests pesados concurrentes del tenant "noisy"
    HEAVY_TOTAL = 500         # total de requests pesados
    NORMAL_SAMPLES = 100      # muestras de latencia del tenant "normal"

    def test_noisy_neighbor_isolation(self):
        tenant_noisy = create_test_tenant("noisy")
        tenant_normal = create_test_tenant("normal")

        # Medir baseline del tenant normal (sin carga concurrente)
        baseline_latencies = self._measure(tenant_normal.id, samples=30)
        baseline_p95 = np.percentile(baseline_latencies, 95) * 1000

        # Someter al tenant noisy a carga pesada concurrente
        # mientras medimos latencia del tenant normal
        latencies_under_load: List[float] = []

        def normal_sample():
            start = time.perf_counter()
            make_normal_request(tenant_normal.id)
            return time.perf_counter() - start

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.CONCURRENT_HEAVY) as ex:
            # Lanzar carga pesada
            heavy_futures = [
                ex.submit(make_heavy_request, tenant_noisy.id)
                for _ in range(self.HEAVY_TOTAL)
            ]
            # Medir concurrentemente
            for _ in range(self.NORMAL_SAMPLES):
                latencies_under_load.append(normal_sample())
            # Esperar a que termine todo
            concurrent.futures.wait(heavy_futures)

        p95_under_load = np.percentile(latencies_under_load, 95) * 1000

        # El p95 bajo carga no debe exceder 2x el baseline ni el SLO absoluto
        max_allowed = min(self.BASELINE_P95_MS, baseline_p95 * 2.0)

        assert p95_under_load <= max_allowed, (
            f"❌ Noisy neighbor detectado:\n"
            f"  Tenant normal p95 baseline:    {baseline_p95:.1f} ms\n"
            f"  Tenant normal p95 bajo carga:  {p95_under_load:.1f} ms\n"
            f"  Máximo permitido:              {max_allowed:.1f} ms\n"
            f"Revisar aislamiento de recursos (DB connections, CPU, memory)."
        )

    def _measure(self, tenant_id: str, samples: int) -> List[float]:
        out = []
        for _ in range(samples):
            s = time.perf_counter()
            make_normal_request(tenant_id)
            out.append(time.perf_counter() - s)
        return out


# ------------------------------------------------------------
# Test de aislamiento de conexiones DB
# ------------------------------------------------------------

class TestDBConnectionIsolation:
    """Verifica que un tenant no puede agotar el pool de conexiones."""

    def test_connection_pool_per_tenant(self):
        # Implementación: verificar que pg_stat_activity muestra conexiones
        # separadas y que ningún tenant consume >20% del pool.
        pytest.skip("Requiere acceso a pg_stat_activity en staging")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
