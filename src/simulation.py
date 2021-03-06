"""
simulation.py -- Specifies different models of simulation.
"""
import tensorflow as tf
import numpy as np
import tqdm


def nbody(m, d=2, G=6.67408e-11,eps_radius=0.001):
    """
    Represents the n-body differential equations.
    """
    with tf.variable_scope("nbody"):
        n = m.get_shape().as_list()[-1]
        M = tf.reshape(tf.tile(m, [n]), [n,n])
        GMtilde = M - tf.diag(m)

        def _dif_eq(t, pv):
            with tf.variable_scope("acceleration"):
                v = pv[n:,:]
                p = pv[:n,:]
                # pi_j - p_ij
                pairmat = tf.reshape(tf.tile(p, [n,1]), [n,n,d])
                pairdif = pairmat - tf.einsum('ijk->jik', pairmat)

                # division s
                iradius = 1/tf.maximum(tf.pow(
                    tf.einsum('ijk,ijk->ij', pairdif, pairdif), 1.5), eps_radius) 
                
                acceleration_direct = tf.einsum('ijk,ij->ijk', pairdif ,iradius)
                dv = G*tf.einsum('ijk,ij->ik',
                                acceleration_direct, 
                                GMtilde) # Todo verify

            with tf.variable_scope("velocity"):
                dp = v 

            return tf.concat([dp, dv], axis=0)

    return _dif_eq



def RK4(f, y0, tmax, h=0.1):
    """
    Implements the Rk4 method."""
    with tf.variable_scope("RK4"):
        y = [y0]
        tint = np.linspace(h, tmax, tmax/h)
        for tn in tqdm.tqdm(tint[1:]):
            with tf.variable_scope("step_{}".format(tn)):
                yn = y[-1]
                
                with tf.variable_scope("k1"):
                    k1 = f(tn, yn)
                with tf.variable_scope("k2"):
                    k2 = f(tn + h/2, yn + h/2*k1)
                with tf.variable_scope("k3"):
                    k3 = f(tn + h/2, yn + h/2*k2)
                with tf.variable_scope("k4"):
                    k4 = f(tn +h, yn + h*k3)
                
                y.append(yn + h/6*(k1+2*k2+2*k3+k4))

    return tint, y
