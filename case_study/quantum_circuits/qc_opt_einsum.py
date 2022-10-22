# -*- coding: UTF-8 -*-
import opt_einsum as oe

import numpy as np

from timeit import default_timer as timer

# tensors for the compuatation
T0 = np.array([1. + 0.j, 0. + 0.j])
T1 = np.array([[0.5 + 0.5j, 0.5 - 0.5j], [0.5 - 0.5j, 0.5 + 0.5j]])
T2 = np.array([[0.70710678 - 0.j, -0.5 - 0.5j], [0.5 - 0.5j, 0.70710678 - 0.j]])
T3 = np.array([[0.5 + 0.5j, -0.5 - 0.5j], [0.5 + 0.5j, 0.5 + 0.5j]])

# einsum string for the opt_einsum compuation
einsum_notation = 'a,b,ca,db,ec,fd,ge,hf,ig,jh,ki,lj,mk,nl,om,pn,qo,rp,sq,tr,us,vt,wu,xv,yw,zx,Ay,Bz,CA,DB,EC,FD,GE,HF,IG,JH,KI,LJ->KL'

# precomputed path for the opt_einsum calculation and the sql code generation
path_info = [((11, 9), {'j'}, 'lj,jh->lh', None, 'GEMM'), ((3, 1), {'b'}, 'db,b->d', None, 'GEMM'), ((24, 22), {'A'}, 'CA,Ay->Cy', None, 'GEMM'), ((33, 3), {'d'}, 'd,fd->f', None, 'GEMM'), ((7, 6), {'k'}, 'mk,ki->mi', None, 'GEMM'), ((1, 0), {'a'}, 'ca,a->c', None, 'GEMM'), ((17, 16), {'z'}, 'Bz,zx->Bx', None, 'GEMM'), ((30, 14), {'x'}, 'Bx,xv->Bv', None, 'GEMM'), ((14, 13), {'w'}, 'yw,wu->yu', None, 'GEMM'), ((27, 13), {'B'}, 'Bv,DB->vD', None, 'GEMM'), ((18, 16), {'H'}, 'JH,HF->JF', None, 'GEMM'), ((1, 0), {'e'}, 'ge,ec->gc', None, 'GEMM'), ((25, 1), {'g'}, 'gc,ig->ci', None, 'GEMM'), ((16, 0), {'h'}, 'lh,hf->lf', None, 'GEMM'), ((22, 18), {'c'}, 'ci,c->i', None, 'GEMM'), ((20, 10), {'F'}, 'JF,FD->JD', None, 'GEMM'), ((4, 2), {'p'}, 'rp,pn->rn', None, 'GEMM'), ((2, 1), {'o'}, 'qo,om->qm', ('nl', 'sq', 'tr', 'us', 'vt', 'EC', 'GE', 'IG', 'KI', 'LJ', 'Cy', 'f', 'mi', 'yu', 'vD', 'lf', 'i', 'JD', 'rn', 'qm'), 'GEMM'), ((18, 2), {'r'}, 'rn,tr->nt', ('nl', 'sq', 'us', 'vt', 'EC', 'GE', 'IG', 'KI', 'LJ', 'Cy', 'f', 'mi', 'yu', 'vD', 'lf', 'i', 'JD', 'qm', 'nt'), 'GEMM'), ((14, 10), {'f'}, 'lf,f->l', ('nl', 'sq', 'us', 'vt', 'EC', 'GE', 'IG', 'KI', 'LJ', 'Cy', 'mi', 'yu', 'vD', 'i', 'JD', 'qm', 'nt', 'l'), 'GEMM'), ((16, 3), {'t'}, 'nt,vt->nv', ('nl', 'sq', 'us', 'EC', 'GE', 'IG', 'KI', 'LJ', 'Cy', 'mi', 'yu', 'vD', 'i', 'JD', 'qm', 'l', 'nv'), 'GEMM'), ((15, 0), {'l'}, 'l,nl->n', ('sq', 'us', 'EC', 'GE', 'IG', 'KI', 'LJ', 'Cy', 'mi', 'yu', 'vD', 'i', 'JD', 'qm', 'nv', 'n'), 'GEMM'), ((15, 14), {'n'}, 'n,nv->v', ('sq', 'us', 'EC', 'GE', 'IG', 'KI', 'LJ', 'Cy', 'mi', 'yu', 'vD', 'i', 'JD', 'qm', 'v'), 'GEMM'), ((7, 2), {'C'}, 'Cy,EC->yE', ('sq', 'us', 'GE', 'IG', 'KI', 'LJ', 'mi', 'yu', 'vD', 'i', 'JD', 'qm', 'v', 'yE'), 'GEMM'), ((9, 6), {'i'}, 'i,mi->m', ('sq', 'us', 'GE', 'IG', 'KI', 'LJ', 'yu', 'vD', 'JD', 'qm', 'v', 'yE', 'm'), 'GEMM'), ((11, 6), {'y'}, 'yE,yu->Eu', ('sq', 'us', 'GE', 'IG', 'KI', 'LJ', 'vD', 'JD', 'qm', 'v', 'm', 'Eu'), 'GEMM'), ((11, 2), {'E'}, 'Eu,GE->uG', ('sq', 'us', 'IG', 'KI', 'LJ', 'vD', 'JD', 'qm', 'v', 'm', 'uG'), 'GEMM'), ((6, 4), {'J'}, 'JD,LJ->DL', ('sq', 'us', 'IG', 'KI', 'vD', 'qm', 'v', 'm', 'uG', 'DL'), 'GEMM'), ((6, 4), {'v'}, 'v,vD->D', ('sq', 'us', 'IG', 'KI', 'qm', 'm', 'uG', 'DL', 'D'), 'GEMM'), ((4, 0), {'q'}, 'qm,sq->ms', ('us', 'IG', 'KI', 'm', 'uG', 'DL', 'D', 'ms'), 'GEMM'), ((7, 3), {'m'}, 'ms,m->s', ('us', 'IG', 'KI', 'uG', 'DL', 'D', 's'), 'GEMM'), ((3, 0), {'u'}, 'uG,us->Gs', ('IG', 'KI', 'DL', 'D', 's', 'Gs'), 'GEMM'), ((5, 4), {'s'}, 'Gs,s->G', ('IG', 'KI', 'DL', 'D', 'G'), 'GEMM'), ((4, 0), {'G'}, 'G,IG->I', ('KI', 'DL', 'D', 'I'), 'GEMM'), ((2, 1), {'D'}, 'D,DL->L', ('KI', 'I', 'L'), 'GEMM'), ((1, 0), {'I'}, 'I,KI->K', ('L', 'K'), 'GEMM'), ((1, 0), set(), 'K,L->KL', ('KL',), 'OUTER/EINSUM')]
path = [i[0] for i in path_info]


# opt_einsum computation
def opt_einsum_discussion():
    tic = timer()
    oe_result = oe.contract(einsum_notation, T0, T0, T1, T1, T2, T2, T2, T1, T1, T3, T3, T3, T1, T2, T2, T3, T2, T1, T1,
                            T1, T2, T3, T2, T3, T3, T3, T2, T2, T1, T3, T1, T2, T3, T1, T2, T3, T2, T1, optimize = path)
    toc = timer()
    print(f"opt_einsum result: {oe_result} (computated in {toc - tic}s)")
    return toc - tic


if __name__ == "__main__":
    opt_einsum_discussion()
