using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Rocket : MonoBehaviour
{
    Rigidbody rigidBody;
    AudioSource aSrc;

    [SerializeField] float rcsThrust = 100f;
    [SerializeField] float thrust = 100f;

    // Start is called before the first frame update
    void Start()
    {
        rigidBody = GetComponent<Rigidbody>();
        aSrc = GetComponent<AudioSource>();

        Vector3 com = rigidBody.centerOfMass;
        rigidBody.centerOfMass = new Vector3(com.x, com.y, 0f);
    }

    // Update is called once per frame
    void Update()
    {
        Thrust();
        Rotate();
    }

    void OnCollisionEnter(Collision collision)
    {
        switch (collision.gameObject.tag) {
            case "Friendly":
                break;
            case "Fuel":
                print("refueling");
                break;
            default:
                Dead();
                break;
        }

    }

    private void Dead()
    {
        print("Dead");
    }

    private void Thrust()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            aSrc.Play();
        }
        if (Input.GetKeyUp(KeyCode.Space))
        {
            aSrc.Pause();
        }

        if (Input.GetKey(KeyCode.Space))
        {
            rigidBody.AddRelativeForce(Vector3.up * thrust);
        }
    }

    private void Rotate()
    {
        rigidBody.freezeRotation = true;
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            transform.Rotate(Vector3.forward * rcsThrust * Time.deltaTime);
        }
        else if (Input.GetKey(KeyCode.RightArrow))
        {
            transform.Rotate(-Vector3.forward * rcsThrust * Time.deltaTime);
        }
        rigidBody.freezeRotation = false;
    }
}
