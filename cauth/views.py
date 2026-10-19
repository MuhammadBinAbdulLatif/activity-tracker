from django.db import DatabaseError
from django.shortcuts import render
from rest_framework import views
from django.contrib.auth.models import User
from cauth.serializers import LoginSerializer, SignUpSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
# creating basic auth


class SignUp(views.APIView):
    def post(self, req):
        data = req.data
        # pass it through the serializer

        serializer = SignUpSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # create the user
            try:
                User.objects.create_user(
                    username=serializer.validated_data["username"],
                    password=serializer.validated_data["password"],
                )
            except DatabaseError as Error:
                return Response(
                    {
                        "success": False,
                        "message": f"An error concering the database has occurred: {Error}",
                    }
                )  # Success of false already points to an error, no need for a separate field
            # check if the user was created
            # if no error was created

            return Response(
                {"success": True, "message": "User was successfully created"},
                status=201,
            )


class Login(views.APIView):
    def post(self, req):
        data = req.data
        # pass it through the serializer

        serializer = LoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # check if the given credentials correctly match the database
            try:
                user = authenticate(
                    request=req,
                    username=serializer.validated_data["username"],
                    password=serializer.validated_data["password"],
                )

            except DatabaseError as Error:
                return Response(
                    {
                        "success": False,
                        "message": f"An error concering the database has occurred: {Error}",
                    },
                    status=409,
                )  # Success of false already points to an error, no need for a separate field
            if user is not None:
                # create the token as I would like to use token authentication
                # just for the sake of it, we are abandoning JWT for this project
                t = Token.objects.create(user=user)
                # send the token back to the user in the response
                return Response(
                    {
                        "success": True,
                        "message": "Token generated successfully",
                        "key": t.key,
                    }
                )

            return Response(
                {"success": False, "message": "Invalid credentials. No user found"}
            )
